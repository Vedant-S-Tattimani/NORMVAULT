import cv2
import numpy as np
import os

def generate_hero():
    src_path = r'C:\Users\Lenovo\.gemini\antigravity-ide\brain\dc1bf6b2-4892-42aa-ac84-18350561f17e\clean_reference_artwork_1790524015071.jpg'
    img = cv2.imread(src_path)
    if img is None:
        raise FileNotFoundError(f"Source artwork not found at {src_path}")
    
    h, w, _ = img.shape
    print(f"Loaded clean reference artwork ({w}x{h}).")

    # =========================================================================
    # STEP 1: Inpaint corner text areas on background canvas
    # (Leaves clean painterly sky/clothing textures so React HTML renders crisp,
    # solid typography without any double-text ghosting across all 21 languages)
    # =========================================================================
    mask = np.zeros((h, w), dtype=np.uint8)

    # 1a. Left flanking metadata (y: 330..535, x: 18..160)
    patch_lm = img[330:535, 18:160]
    gray_lm = cv2.cvtColor(patch_lm, cv2.COLOR_BGR2GRAY)
    mask_lm = np.zeros_like(gray_lm)
    mask_lm[gray_lm < 100] = 255
    mask[330:535, 18:160] = cv2.dilate(mask_lm, np.ones((3, 3), np.uint8), iterations=2)

    # 1b. Right flanking metadata (y: 330..535, x: 1215..1365)
    patch_rm = img[330:535, 1215:1365]
    gray_rm = cv2.cvtColor(patch_rm, cv2.COLOR_BGR2GRAY)
    mask_rm = np.zeros_like(gray_rm)
    mask_rm[gray_rm < 105] = 255
    mask[330:535, 1215:1365] = cv2.dilate(mask_rm, np.ones((3, 3), np.uint8), iterations=2)

    # 1c. Bottom left signature (y: 695..760, x: 15..365)
    patch_bl = img[695:760, 15:365]
    gray_bl = cv2.cvtColor(patch_bl, cv2.COLOR_BGR2GRAY)
    mask_bl = np.zeros_like(gray_bl)
    mask_bl[gray_bl > 80] = 255
    mask[695:760, 15:365] = cv2.dilate(mask_bl, np.ones((3, 3), np.uint8), iterations=2)

    # 1d. Bottom right signature (y: 695..760, x: 1005..1365)
    patch_br = img[695:760, 1005:1365]
    gray_br = cv2.cvtColor(patch_br, cv2.COLOR_BGR2GRAY)
    mask_br = np.zeros_like(gray_br)
    mask_br[gray_br > 85] = 255
    mask[695:760, 1005:1365] = cv2.dilate(mask_br, np.ones((3, 3), np.uint8), iterations=2)

    inpainted = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    print("Step 1: Cleaned corner text areas for zero-ghosting HTML overlays.")

    # =========================================================================
    # STEP 2: Color Saturation & High Contrast Calibration
    # Rich teal-blue sky at edges, warm gold/amber foliage, muted earthy greens.
    # No soft-focus, no fog wash, no blur.
    # =========================================================================
    hsv = cv2.cvtColor(inpainted, cv2.COLOR_BGR2HSV).astype(np.float32)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # 2a. Rich teal-blue sky at the edges (Hue 72..135)
    sky_mask = np.clip((H - 72.0) / 8.0, 0, 1) * np.clip((135.0 - H) / 8.0, 0, 1)
    dist_from_center_x = np.abs(np.arange(w) - w / 2.0) / (w / 2.0)
    dist_grid = np.tile(dist_from_center_x, (h, 1))
    sky_edge_weight = np.clip(dist_grid * 1.3, 0.4, 1.0) * sky_mask
    S = np.where(sky_mask > 0, S * (1.0 + 0.22 * sky_edge_weight), S)

    # 2b. Warm gold/amber autumn foliage (Hue 9..38)
    warm_mask = np.clip((H - 9.0) / 6.0, 0, 1) * np.clip((38.0 - H) / 6.0, 0, 1)
    S = np.where(warm_mask > 0, np.clip(S * 1.20 + 8.0, 0, 255), S)

    # 2c. Muted earthy greens (Hue 36..72)
    green_mask = np.clip((H - 36.0) / 5.0, 0, 1) * np.clip((72.0 - H) / 5.0, 0, 1)
    S = np.where(green_mask > 0, np.clip(S * 1.15 + 4.0, 0, 255), S)

    hsv[:, :, 0] = np.clip(H, 0, 179)
    hsv[:, :, 1] = np.clip(S, 0, 255)
    hsv[:, :, 2] = np.clip(V, 0, 255)

    graded = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

    # 2d. High Contrast: S-curve to achieve crisp contrast between elements
    norm = graded / 255.0
    contrast_tuned = np.where(
        norm < 0.5,
        2.0 * (norm ** 1.12) * 0.5,
        1.0 - 2.0 * ((1.0 - norm) ** 1.08) * 0.5
    )
    result = np.clip(contrast_tuned * 255.0, 0, 255).astype(np.uint8)

    # =========================================================================
    # STEP 3: Save final calibrated artwork
    # =========================================================================
    target_path = 'public/hero_editorial_canvas.jpg'
    cv2.imwrite(target_path, result, [int(cv2.IMWRITE_JPEG_QUALITY), 96])
    print(f"Step 3: Saved final calibrated hero artwork to {target_path} successfully!")

if __name__ == '__main__':
    generate_hero()
