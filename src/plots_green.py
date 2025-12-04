import argparse, json, os, glob, csv
import cv2
import numpy as np
from PIL import Image, ImageOps

WIN_NAME = "Plot Selector"
TUNE_WIN = "HSV Tuner"
STROKE_STACK_LIMIT = 30  # undo depth for exclusion painting

# ---------- EXIF-safe image loading ----------
def imread_exif_safe(path):
    """Read an image honoring EXIF rotation, return BGR array for OpenCV."""
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)
        im = im.convert("RGB")
        arr = np.array(im)  # RGB
    return arr[:, :, ::-1].copy()  # to BGR

# ---------- Orientation helpers ----------
def rotate90(img, k=1):
    k = k % 4
    if k == 1: return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if k == 2: return cv2.rotate(img, cv2.ROTATE_180)
    if k == 3: return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img
def flip_h(img): return cv2.flip(img, 1)
def flip_v(img): return cv2.flip(img, 0)

# ---------- Window / UI helpers ----------
def ensure_window(win_name, disp):
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, min(1200, disp.shape[1]), min(900, disp.shape[0]))
    if cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) == -1:
        raise RuntimeError("OpenCV GUI backend not available. Try: QT_QPA_PLATFORM=xcb python ...")

def draw_instructions(img, allow_prev=False):
    msg = "Click 4 corners: Enter=accept  u=undo  r=reset  s=skip  q=quit  a/d=rot90  h=flipH  v=flipV"
    if allow_prev:
        msg += "  p=prev"
    vis = img.copy()
    cv2.rectangle(vis, (10, 10), (10 + 8 * len(msg), 40), (0, 0, 0), -1)
    cv2.putText(vis, msg, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
    return vis

# ---------- Geometry ----------
def order_points(pts):
    pts = np.array(pts, dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).ravel()
    ordered = np.zeros((4, 2), dtype="float32")
    ordered[0] = pts[np.argmin(s)]
    ordered[2] = pts[np.argmax(s)]
    ordered[1] = pts[np.argmin(diff)]
    ordered[3] = pts[np.argmax(diff)]
    return ordered

def auto_output_size(pts):
    (tl, tr, br, bl) = pts
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    width = int(max(widthA, widthB))
    height = int(max(heightA, heightB))
    return max(100, min(4000, width)), max(100, min(4000, height))

def perspective_rectify(img, pts, out_w=None, out_h=None):
    pts = order_points(pts)
    if out_w is None or out_h is None:
        out_w, out_h = auto_output_size(pts)
    dst = np.float32([[0, 0], [out_w - 1, 0],
                      [out_w - 1, out_h - 1], [0, out_h - 1]])
    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, M, (out_w, out_h))
    return warped, (out_w, out_h)

# ---------- Mask & overlay ----------
def quantify_green_with_thresholds(img_bgr, lower, upper, open_iters=1):
    img = cv2.medianBlur(img_bgr, 3)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower, np.uint8), np.array(upper, np.uint8))
    if open_iters > 0:
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=open_iters)
    green_pixels = int(np.count_nonzero(mask))
    percent = 100.0 * green_pixels / mask.size if mask.size else 0.0
    return percent, mask

def overlay_mask(warped, mask):
    overlay = warped.copy()
    green_tint = np.zeros_like(overlay)
    green_tint[:, :, 1] = mask
    return cv2.addWeighted(overlay, 1.0, green_tint, 0.4, 0)

def draw_points_preview(img, pts):
    vis = img.copy()
    for i, p in enumerate(pts):
        cv2.circle(vis, p, 6, (0, 0, 255), -1)
        cv2.putText(vis, str(i+1), (p[0]+6, p[1]-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    if len(pts) == 4:
        cv2.polylines(vis, [np.array(pts, np.int32)], True, (0, 255, 255), 2)
    return vis

# ---------- Mouse handler for corner selection ----------
class Clicker:
    def __init__(self, window):
        self.points = []
        cv2.setMouseCallback(window, self.on_mouse)
    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
    def reset(self): self.points = []
    def undo(self):
        if self.points: self.points.pop()

# ---------- HSV tuner (trackbars + brush + Shift+drag rectangles) ----------
def create_hsv_tuner(initial_lower, initial_upper):
    cv2.namedWindow(TUNE_WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(TUNE_WIN, 520, 360)
    cv2.createTrackbar("H_min", TUNE_WIN, initial_lower[0], 180, lambda v: None)
    cv2.createTrackbar("S_min", TUNE_WIN, initial_lower[1], 255, lambda v: None)
    cv2.createTrackbar("V_min", TUNE_WIN, initial_lower[2], 255, lambda v: None)
    cv2.createTrackbar("H_max", TUNE_WIN, initial_upper[0], 180, lambda v: None)
    cv2.createTrackbar("S_max", TUNE_WIN, initial_upper[1], 255, lambda v: None)
    cv2.createTrackbar("V_max", TUNE_WIN, initial_upper[2], 255, lambda v: None)

def get_hsv_from_trackbar():
    h_min = cv2.getTrackbarPos("H_min", TUNE_WIN)
    s_min = cv2.getTrackbarPos("S_min", TUNE_WIN)
    v_min = cv2.getTrackbarPos("V_min", TUNE_WIN)
    h_max = cv2.getTrackbarPos("H_max", TUNE_WIN)
    s_max = cv2.getTrackbarPos("S_max", TUNE_WIN)
    v_max = cv2.getTrackbarPos("V_max", TUNE_WIN)
    h_min, h_max = min(h_min, h_max), max(h_min, h_max)
    s_min, s_max = min(s_min, s_max), max(s_min, s_max)
    v_min, v_max = min(v_min, v_max), max(v_min, v_max)
    return [h_min, s_min, v_min], [h_max, s_max, v_max]

def tune_thresholds_on_image(warped, lower, upper, exclude_path=None):
    """
    HSV tuner with exclusions:
      - LEFT drag           : brush (paint/erase toggle with 'b')
      - SHIFT + LEFT drag   : add a rectangular exclusion (always adds)
    Keys:
      Enter=accept, c=cycle view, b=toggle brush paint/erase,
      [ / ] brush size, u=undo, x=clear, m=toggle excl overlay, q/ESC=accept
    Saves exclusion PNG if exclude_path is given.
    """
    ensure_window(TUNE_WIN, warped)
    create_hsv_tuner(lower, upper)

    # Exclusion mask (uint8, 0=keep, 255=exclude)
    exclude_mask = np.zeros(warped.shape[:2], np.uint8)
    if exclude_path and os.path.exists(exclude_path):
        try:
            m = cv2.imread(exclude_path, cv2.IMREAD_GRAYSCALE)
            if m is not None and m.shape == exclude_mask.shape:
                exclude_mask = (m > 0).astype(np.uint8) * 255
        except Exception:
            pass

    # State
    brush_radius = 20
    painting_mode = 1  # 1=paint(exclude), 0=erase(include) for LEFT-brush
    show_excl = True
    show_mode = 0  # 0 overlay, 1 mask-only, 2 image-only

    # Mouse interaction state
    drawing_paint = False      # brush with LEFT
    rect_active = False        # SHIFT+LEFT rectangle drag
    rect_start = (0, 0)
    rect_end = (0, 0)

    # Undo stack
    undo_stack = []
    def push_undo():
        nonlocal undo_stack
        if len(undo_stack) >= STROKE_STACK_LIMIT:
            undo_stack.pop(0)
        undo_stack.append(exclude_mask.copy())

    # Mouse callback: LEFT = brush; SHIFT+LEFT = rectangle add
    def on_mouse(event, x, y, flags, param):
        nonlocal drawing_paint, rect_active, rect_start, rect_end

        shift_down = (flags & cv2.EVENT_FLAG_SHIFTKEY) != 0

        # ----- SHIFT + LEFT: rectangle add (always adds exclusion) -----
        if shift_down:
            if event == cv2.EVENT_LBUTTONDOWN:
                push_undo()
                rect_active = True
                rect_start = (x, y)
                rect_end = (x, y)
            elif event == cv2.EVENT_MOUSEMOVE and rect_active:
                rect_end = (x, y)
            elif event == cv2.EVENT_LBUTTONUP and rect_active:
                rect_end = (x, y)
                rect_active = False
                # apply rectangle to exclusion mask (clamped)
                x1, y1 = rect_start; x2, y2 = rect_end
                x1 = max(0, min(x1, exclude_mask.shape[1]-1))
                x2 = max(0, min(x2, exclude_mask.shape[1]-1))
                y1 = max(0, min(y1, exclude_mask.shape[0]-1))
                y2 = max(0, min(y2, exclude_mask.shape[0]-1))
                x1, x2 = sorted((x1, x2)); y1, y2 = sorted((y1, y2))
                if x2 > x1 and y2 > y1:
                    cv2.rectangle(exclude_mask, (x1, y1), (x2, y2), 255, -1, lineType=cv2.LINE_AA)

        # ----- Regular LEFT: brush paint/erase -----
        else:
            if event == cv2.EVENT_LBUTTONDOWN:
                push_undo()
                drawing_paint = True
                color = 255 if painting_mode == 1 else 0
                cv2.circle(exclude_mask, (x, y), brush_radius, color, -1, lineType=cv2.LINE_AA)
            elif event == cv2.EVENT_MOUSEMOVE and drawing_paint:
                color = 255 if painting_mode == 1 else 0
                cv2.circle(exclude_mask, (x, y), brush_radius, color, -1, lineType=cv2.LINE_AA)
            elif event == cv2.EVENT_LBUTTONUP:
                drawing_paint = False

    cv2.setMouseCallback(TUNE_WIN, on_mouse)

    while True:
        lower_t, upper_t = get_hsv_from_trackbar()
        _, raw_mask = quantify_green_with_thresholds(warped, lower_t, upper_t, open_iters=1)

        # Apply exclusions
        combined_mask = raw_mask.copy()
        if np.any(exclude_mask):
            combined_mask[exclude_mask > 0] = 0

        # Base view
        if show_mode == 0:
            view = overlay_mask(warped, combined_mask); mode_str = "overlay"
        elif show_mode == 1:
            view = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR); mode_str = "mask"
        else:
            view = warped.copy(); mode_str = "image"

        # Rectangle preview (semi-transparent red) while dragging
        if rect_active:
            x1, y1 = rect_start; x2, y2 = rect_end
            preview = np.zeros_like(view)
            cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 0, 255), -1, lineType=cv2.LINE_AA)
            view = cv2.addWeighted(view, 1.0, preview, 0.25, 0)
            cv2.rectangle(view, (x1, y1), (x2, y2), (0, 0, 255), 2, lineType=cv2.LINE_AA)

        # Exclusion overlay (semi-transparent red)
        if show_excl and np.any(exclude_mask):
            excl_rgb = np.zeros_like(view)
            excl_rgb[:, :, 2] = exclude_mask
            view = cv2.addWeighted(view, 1.0, excl_rgb, 0.35, 0)

        hud = (
            f"HSV tuner [{mode_str}]  Enter=accept  c=cycle   "
            f"SHIFT+LEFT-drag=rect add   LEFT-drag={'paint' if painting_mode else 'erase'}   "
            f"[ / ] brush  b=toggle paint/erase  u=undo  x=clear  m=toggle excl  q/ESC=accept   "
            f"brush={brush_radius}"
        )
        cv2.rectangle(view, (10, 10), (10 + 8*len(hud), 40), (0,0,0), -1)
        cv2.putText(view, hud, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
        cv2.imshow(TUNE_WIN, view)

        key = cv2.waitKey(30) & 0xFF
        if key == 13:  # Enter
            lower, upper = lower_t, upper_t
            break
        elif key in (27, ord('q')):
            lower, upper = lower_t, upper_t
            break
        elif key == ord('c'):
            show_mode = (show_mode + 1) % 3
        elif key == ord('b'):
            painting_mode ^= 1  # affects LEFT brush
        elif key in (ord('['), ord('{')):
            brush_radius = max(1, brush_radius - 2)
        elif key in (ord(']'), ord('}')):
            brush_radius = min(200, brush_radius + 2)
        elif key == ord('x'):
            push_undo()
            exclude_mask[:] = 0
        elif key == ord('u') and undo_stack:
            exclude_mask[:] = undo_stack.pop()
        elif key == ord('m'):
            show_excl = not show_excl

    cv2.destroyWindow(TUNE_WIN)
    if exclude_path is not None:
        try:
            cv2.imwrite(exclude_path, exclude_mask)
        except Exception:
            pass
    return lower, upper, exclude_mask

# ---------- Per-image processing ----------
def process_image(img_path, args, thresholds_store, allow_prev=False):
    img = imread_exif_safe(img_path)
    disp = img.copy()
    ops = []

    ensure_window(WIN_NAME, disp)
    clicker = Clicker(WIN_NAME)

    # --- rotate/flip + pick 4 points ---
    while True:
        vis = draw_instructions(disp, allow_prev)
        vis = draw_points_preview(vis, clicker.points)
        cv2.imshow(WIN_NAME, vis)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('u'): clicker.undo()
        elif key == ord('r'): clicker.reset()
        elif key == ord('s'):
            cv2.destroyWindow(WIN_NAME)
            print(f"[SKIP] {os.path.basename(img_path)}")
            return "skip", None
        elif key == ord('p') and allow_prev:
            cv2.destroyWindow(WIN_NAME)
            print(f"[BACK] Re-opening previous image before {os.path.basename(img_path)}")
            return "back", None
        elif key in (27, ord('q')):
            cv2.destroyAllWindows()
            raise KeyboardInterrupt
        elif key == ord('a'):
            disp = rotate90(disp, 3); ops.append(('rot', 3)); clicker.reset()
            cv2.resizeWindow(WIN_NAME, min(1200, disp.shape[1]), min(900, disp.shape[0]))
        elif key == ord('d'):
            disp = rotate90(disp, 1); ops.append(('rot', 1)); clicker.reset()
            cv2.resizeWindow(WIN_NAME, min(1200, disp.shape[1]), min(900, disp.shape[0]))
        elif key == ord('h'):
            disp = flip_h(disp); ops.append(('flip', 'h')); clicker.reset()
        elif key == ord('v'):
            disp = flip_v(disp); ops.append(('flip', 'v')); clicker.reset()
        elif key == 13:
            if len(clicker.points) == 4: break
            else: print("Select exactly 4 points.")

    cv2.destroyWindow(WIN_NAME)

    # Apply ops to original, then rectify
    oriented = img.copy()
    for op, val in ops:
        if op == 'rot': oriented = rotate90(oriented, val)
        else: oriented = flip_h(oriented) if val == 'h' else flip_v(oriented)

    warped, (w, h) = perspective_rectify(oriented, clicker.points, args.width, args.height)

    # Optional normalize BEFORE tuning so tuner shows final orientation
    if args.normalize == "landscape" and warped.shape[0] > warped.shape[1]:
        warped = rotate90(warped, 1)
    elif args.normalize == "portrait" and warped.shape[1] > warped.shape[0]:
        warped = rotate90(warped, 1)

    base = os.path.splitext(os.path.basename(img_path))[0]
    os.makedirs(args.output, exist_ok=True)
    exclude_path = os.path.join(args.output, f"{base}_exclude.png")

    # --- tune thresholds & exclusions (or reuse stored) ---
    lower = thresholds_store["lower"]
    upper = thresholds_store["upper"]
    if args.tune:
        lower, upper, exclude_mask = tune_thresholds_on_image(
            warped, lower, upper, exclude_path=exclude_path
        )
        thresholds_store["lower"] = lower
        thresholds_store["upper"] = upper
        with open(thresholds_store["path"], "w") as f:
            json.dump({"lower": lower, "upper": upper}, f, indent=2)
    else:
        # No tuning: load any existing exclusion mask if present
        exclude_mask = np.zeros(warped.shape[:2], np.uint8)
        if os.path.exists(exclude_path):
            m = cv2.imread(exclude_path, cv2.IMREAD_GRAYSCALE)
            if m is not None and m.shape == exclude_mask.shape:
                exclude_mask = (m > 0).astype(np.uint8) * 255

    # Compute final mask & percent using chosen thresholds AND exclusions
    percent, raw_mask = quantify_green_with_thresholds(warped, lower, upper, open_iters=1)
    final_mask = raw_mask.copy()
    final_mask[exclude_mask > 0] = 0

    overlay = overlay_mask(warped, final_mask)

    # Save outputs
    cv2.imwrite(os.path.join(args.output, f"{base}_rectified.jpg"), warped)
    cv2.imwrite(os.path.join(args.output, f"{base}_mask.png"), final_mask)
    cv2.imwrite(os.path.join(args.output, f"{base}_overlay.jpg"), overlay)
    with open(os.path.join(args.output, f"{base}_corners.json"), "w") as f:
        json.dump({"points_xy": clicker.points, "ops": ops,
                   "thresholds": {"lower": lower, "upper": upper}}, f, indent=2)

    result_row = {
        "image": os.path.basename(img_path),
        "percent_green": f"{percent:.3f}",
        "rect_width": str(warped.shape[1]),
        "rect_height": str(warped.shape[0]),
    }
    print(f"[OK] {result_row['image']} → {percent:.2f}% green, size={warped.shape[1]}x{warped.shape[0]}")
    return "success", result_row

# ---------- Progress tracking ----------
def load_progress(output_dir):
    """Load list of already processed images."""
    progress_file = os.path.join(output_dir, ".progress.json")
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r") as f:
                data = json.load(f)
                return set(data.get("processed", []))
        except Exception:
            pass
    return set()

def save_progress(output_dir, processed_images):
    """Save list of processed images."""
    progress_file = os.path.join(output_dir, ".progress.json")
    try:
        with open(progress_file, "w") as f:
            json.dump({"processed": sorted(list(processed_images))}, f, indent=2)
    except Exception:
        pass

def get_existing_results(csv_path):
    """Load existing results from CSV."""
    existing = {}
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing[row["image"]] = row
        except Exception:
            pass
    return existing

def write_results_csv(csv_path, order, results):
    """Rewrite the results CSV using provided order and data."""
    try:
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["image", "percent_green", "rect_width", "rect_height"])
            for image in order:
                row = results.get(image)
                if not row:
                    continue
                writer.writerow([
                    image,
                    row.get("percent_green", ""),
                    row.get("rect_width", ""),
                    row.get("rect_height", ""),
                ])
    except Exception:
        pass

SUPPORTED_PATTERNS = ("*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff", "*.bmp")


def image_base_name(path):
    return os.path.splitext(os.path.basename(path))[0]


def gather_input_images(input_path):
    if os.path.isfile(input_path):
        return [input_path]
    if os.path.isdir(input_path):
        images = []
        for pattern in SUPPORTED_PATTERNS:
            images.extend(glob.glob(os.path.join(input_path, pattern)))
        images.sort()
        return images
    raise FileNotFoundError(f"Input path not found: {input_path}")


def discover_processed_images(output_dir):
    suffixes = ("_rectified.jpg", "_mask.png", "_overlay.jpg", "_corners.json")
    processed = set()
    if not os.path.isdir(output_dir):
        return processed
    for suffix in suffixes:
        pattern = os.path.join(output_dir, f"*{suffix}")
        for path in glob.glob(pattern):
            base = os.path.basename(path)
            if base.endswith(suffix):
                processed.add(base[:-len(suffix)])
    return processed

# ---------- Main loop ----------
def main():
    ap = argparse.ArgumentParser(description="Interactive plot rectification & green quantification with HSV tuner + exclusions")
    ap.add_argument("--input", required=True, help="Image file or folder with input images")
    ap.add_argument("--output", required=True, help="Folder to save results")
    ap.add_argument("--width", type=int, default=None, help="Forced rectified width")
    ap.add_argument("--height", type=int, default=None, help="Forced rectified height")
    ap.add_argument("--normalize", choices=["none", "landscape", "portrait"], default="none",
                    help="Rotate rectified output to desired orientation before tuning")
    ap.add_argument("--tune", action="store_true",
                    help="Open HSV tuner after rectification to adjust thresholds and paint/rect exclude")
    ap.add_argument("--resume", action="store_true",
                    help="(Deprecated) Outputs are auto-detected; flag kept for compatibility")
    args = ap.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Load threshold defaults or last-used values
    th_path = os.path.join(args.output, "hsv_thresholds.json")
    if os.path.exists(th_path):
        try:
            data = json.load(open(th_path, "r"))
            lower = data.get("lower", [35, 40, 40])
            upper = data.get("upper", [85, 255, 255])
        except Exception:
            lower, upper = [35, 40, 40], [85, 255, 255]
    else:
        lower, upper = [35, 40, 40], [85, 255, 255]
    thresholds_store = {"lower": lower, "upper": upper, "path": th_path}

    if args.resume:
        print("[INFO] --resume is deprecated; outputs are checked automatically.")

    # Gather images
    try:
        images = gather_input_images(args.input)
    except FileNotFoundError as exc:
        print(str(exc))
        return
    if not images:
        print("No images found.")
        return

    processed_bases = discover_processed_images(args.output)
    images_to_process = [img for img in images if image_base_name(img) not in processed_bases]
    if not images_to_process:
        print("All images already processed!")
        return

    print(f"\nFound {len(images)} input image(s) in '{args.input}'.")
    already_done = len(images) - len(images_to_process)
    if already_done:
        print(f"Detected {already_done} already processed image(s) in '{args.output}'.")
    print(f"Processing {len(images_to_process)} remaining image(s).")

    csv_path = os.path.join(args.output, "foliage_results.csv")
    existing_results = get_existing_results(csv_path)

    results_order = list(existing_results.keys())

    i = 0
    try:
        while i < len(images_to_process):
            img_path = images_to_process[i]
            status, row = process_image(
                img_path,
                args,
                thresholds_store,
                allow_prev=i > 0,
            )

            if status == "success" and row:
                img_name = row["image"]
                existing_results[img_name] = row
                if img_name not in results_order:
                    results_order.append(img_name)
                write_results_csv(csv_path, results_order, existing_results)
                processed_bases.add(image_base_name(img_name))
                i += 1
            elif status == "skip":
                i += 1
            elif status == "back":
                if i == 0:
                    print("Already at first image; cannot go back further.")
                    continue
                prev_img = images_to_process[i - 1]
                prev_name = os.path.basename(prev_img)
                processed_bases.discard(image_base_name(prev_name))
                if prev_name in existing_results:
                    existing_results.pop(prev_name, None)
                    if prev_name in results_order:
                        results_order.remove(prev_name)
                    write_results_csv(csv_path, results_order, existing_results)
                i -= 1
            else:
                # Shouldn't happen, but advance to avoid infinite loop
                i += 1
    except KeyboardInterrupt:
        print("\n[QUIT] Stopping early. Existing outputs remain intact.")
        print("Re-run the command to continue; images with saved outputs will be skipped automatically.")

if __name__ == "__main__":
    main()
