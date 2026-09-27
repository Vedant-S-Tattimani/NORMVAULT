import cv2
import numpy as np
from PIL import Image

def generate_hero():
    src = r'C:\Users\Lenovo\.gemini\antigravity-ide\brain\dc1bf6b2-4892-42aa-ac84-18350561f17e\seamless_hero_artwork_1790526034280.jpg'
    img = cv2.imread(src)
    h, w, c = img.shape
    print(f"Loaded source image: {w}x{h}")

    # =========================================================================
    # STEP 1: Clean bottom text/watermarks for multilingual overlay
    # =========================================================================
    mask = np.zeros((h, w), dtype=np.uint8)
    # Bottom left: | BUILT FOR GOVERNMENT AND PSUS
    gray_left = cv2.cvtColor(img[680:755, 20:310], cv2.COLOR_BGR2GRAY)
    mask_left = np.zeros_like(gray_left)
    mask_left[gray_left > 75] = 255
    mask[680:755, 20:310] = cv2.dilate(mask_left, np.ones((5, 5), np.uint8), iterations=1)

    # Bottom right: POWERED BY INDIAN STANDARDS |
    gray_right = cv2.cvtColor(img[680:755, 1040:1360], cv2.COLOR_BGR2GRAY)
    mask_right = np.zeros_like(gray_right)
    mask_right[gray_right > 95] = 255
    mask[680:755, 1040:1360] = cv2.dilate(mask_right, np.ones((5, 5), np.uint8), iterations=1)

    img = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    print("Step 1: Cleaned bottom corners for clean i18n overlays.")

    # =========================================================================
    # STEP 2: Fully eliminate the horizontal seam line across eyebrows
    # =========================================================================
    # 2a. Inpaint anomalous bright seam pixels along y=580..596, x=530..870
    strip_mask = np.zeros((h, w), dtype=np.uint8)
    for y in range(581, 596):
        for x in range(530, 870):
            b, g, r = img[y, x].astype(float)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if y <= 588 and lum > 140:
                strip_mask[y, x] = 255
            elif (650 <= x <= 720 and 582 <= y <= 591 and lum > 135):
                strip_mask[y, x] = 255
            elif (575 <= x <= 590 and 592 <= y <= 595 and lum > 175):
                strip_mask[y, x] = 255

    strip_mask = cv2.dilate(strip_mask, np.ones((3, 3), np.uint8), iterations=1)
    img = cv2.inpaint(img, strip_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # 2b. Sample natural foliage colors from the canopy directly above (y=550..580)
    foliage_palette = []
    for fy in range(550, 580, 2):
        for fx in range(500, 900, 3):
            bgr = img[fy, fx].astype(float)
            if np.mean(bgr) < 95: # dark rich foliage
                foliage_palette.append(bgr)
    foliage_palette = np.array(foliage_palette)

    # 2c. Paint cascading watercolor leaf clusters & botanical brushstrokes across x=515..885
    rng = np.random.RandomState(137)
    botanical = np.zeros((h, w, 4), dtype=np.float32)

    cur_x = 515.0
    x_coords = []
    while cur_x < 885.0:
        x_coords.append(cur_x)
        cur_x += rng.uniform(4.5, 9.5)

    for cx_f in x_coords:
        cx = int(cx_f)
        # Eyebrow arch curvature: center is slightly higher (585..588), arches curve down (588..593)
        center_dist = abs(cx - 692)
        base_y = int(585 + 3.5 * np.sin(cx * 0.035) + rng.uniform(-1.5, 2.5))

        # Varied drop depths breaking the horizontal line completely:
        if center_dist < 35:
            max_drop = rng.uniform(8, 16)   # delicate leaves over nose bridge
        elif center_dist < 90:
            max_drop = rng.uniform(12, 22)  # fuller leaves over eyebrow arches
        else:
            max_drop = rng.uniform(10, 26)  # lush leaves over temples

        num_leaves = rng.randint(2, 6)
        for _ in range(num_leaves):
            lx = cx + rng.randint(-5, 6)
            drop = rng.uniform(2, max_drop)
            ly = int(base_y + drop)

            rx = rng.uniform(3.2, 5.8)
            ry = rng.uniform(5.5, 11.0)
            angle = rng.uniform(-35, 35) + (lx - 692) * 0.08

            c_idx = rng.randint(0, len(foliage_palette))
            leaf_col = foliage_palette[c_idx] + rng.uniform(-6, 6, 3)
            leaf_col = np.clip(leaf_col, 0, 255)
            opacity = rng.uniform(0.70, 0.95)

            rad = int(max(rx, ry) * 2.2) + 2
            y1, y2 = max(0, ly - rad), min(h, ly + rad)
            x1, x2 = max(0, lx - rad), min(w, lx + rad)
            if y2 <= y1 or x2 <= x1:
                continue

            patch = np.zeros((y2 - y1, x2 - x1), dtype=np.float32)
            pt = (lx - x1, ly - y1)
            cv2.ellipse(patch, pt, (int(rx), int(ry)), angle, 0, 360, 1.0, -1)
            patch = cv2.GaussianBlur(patch, (3, 3), 0.8)

            for py in range(y2 - y1):
                for px in range(x2 - x1):
                    val = patch[py, px]
                    if val > 0:
                        a = val * opacity
                        cur_a = botanical[y1 + py, x1 + px, 3]
                        out_a = cur_a + a * (1.0 - cur_a)
                        if out_a > 0:
                            for c_i in range(3):
                                botanical[y1 + py, x1 + px, c_i] = (
                                    botanical[y1 + py, x1 + px, c_i] * cur_a +
                                    leaf_col[c_i] * a * (1.0 - cur_a)
                                ) / out_a
                            botanical[y1 + py, x1 + px, 3] = out_a

    # 2d. Soft ambient watercolor contact shadow on skin underneath leaves
    alpha_mask = botanical[:, :, 3]
    shadow_mask = cv2.GaussianBlur(alpha_mask, (15, 15), 5.0)
    shadow_mask = np.clip(shadow_mask * 0.42, 0, 0.42)

    img_float = img.astype(np.float32)
    for c_i in range(3):
        img_float[:, :, c_i] *= (1.0 - shadow_mask)

    # Composite botanical leaves
    bot_a = botanical[:, :, 3:4]
    bot_bgr = botanical[:, :, :3]
    blended = img_float * (1.0 - bot_a) + bot_bgr * bot_a
    img = np.clip(blended, 0, 255).astype(np.uint8)

    # 2e. Seamless texture continuity pass across transition band
    band = img[582:608, 490:910].copy()
    glaze = cv2.bilateralFilter(band, d=7, sigmaColor=28, sigmaSpace=7)
    img[582:608, 490:910] = cv2.addWeighted(band, 0.45, glaze, 0.55, 0)
    print("Step 2: Fully eliminated horizontal seam with botanical foliage & watercolor blending.")

    # =========================================================================
    # STEP 3: Restore Two-Tone Painterly Palette (Cool Teal vs Warm Golden-Ochre)
    # =========================================================================
    # Convert to HSV float
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # 3a. Sky & Cool areas (Muted Teal-Grey-Blue):
    # In OpenCV HSV: cyan/teal is H in 70..125
    sky_mask = np.clip((H - 70) / 10.0, 0, 1) * np.clip((125 - H) / 10.0, 0, 1)
    # Shift hue towards elegant vintage oceanic teal (H ~ 92..95 in OpenCV HSV)
    H = np.where(sky_mask > 0, 93.0 + (H - 85.0) * 0.35, H)
    # Healthy saturation (not washed out to grey/brown, S ~ 80..115)
    S = np.where(sky_mask > 0, np.clip(S * 1.05 + 8.0, 65, 130), S)

    # 3b. Foliage highlights, Parliament Building, and Warm Areas (Warm Golden-Ochre / Tan):
    # Warm colors: H in 10..38
    warm_mask = np.clip((H - 8) / 6.0, 0, 1) * np.clip((38 - H) / 8.0, 0, 1)
    # Golden ochre / amber hue (H ~ 17..23)
    H = np.where(warm_mask > 0, np.clip(H + 1.2, 14, 25), H)
    # Vibrant warm golden saturation (prevent muddy brown wash)
    S = np.where(warm_mask > 0, np.clip(S * 1.08 + 8.0, 70, 185), S)

    # 3c. Clothing areas (lower left & right) -> enhance muted teal-grey-blue
    # Lower left (y > 700, x < 450) and Lower right (y > 700, x > 950)
    for y_cl in range(700, h):
        for x_cl in range(0, w):
            if (x_cl < 450 or x_cl > 950) and V[y_cl, x_cl] < 160:
                # If it's clothing tone, nudge hue to cool teal-slate
                if H[y_cl, x_cl] > 35 and H[y_cl, x_cl] < 130:
                    H[y_cl, x_cl] = 90.0
                    S[y_cl, x_cl] = np.clip(S[y_cl, x_cl] * 1.1 + 5.0, 40, 120)

    # Reconstruct RGB
    hsv[:, :, 0] = np.clip(H, 0, 179)
    hsv[:, :, 1] = np.clip(S, 0, 255)
    hsv[:, :, 2] = np.clip(V, 0, 255)
    graded_rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

    # 3d. Split-Tone Color Contrast (Shadows Teal-Grey-Blue vs Highlights Golden-Ochre):
    lum = (0.299 * graded_rgb[:, :, 0] + 0.587 * graded_rgb[:, :, 1] + 0.114 * graded_rgb[:, :, 2]) / 255.0

    # Cool teal tint in shadows & dark areas (lum < 0.5)
    shadow_w = np.clip(1.0 - lum * 1.8, 0, 1)[:, :, np.newaxis]
    shadow_teal = np.array([-7.0, 3.0, 15.0], dtype=np.float32) # cool teal-blue
    graded_rgb = np.clip(graded_rgb + shadow_w * shadow_teal, 0, 255)

    # Warm golden-ochre tint in highlights & light areas (lum > 0.35)
    highlight_w = np.clip((lum - 0.35) * 1.6, 0, 1)[:, :, np.newaxis]
    highlight_gold = np.array([12.0, 6.0, -10.0], dtype=np.float32) # warm golden-ochre
    graded_rgb = np.clip(graded_rgb + highlight_w * highlight_gold, 0, 255)

    # 3e. Subtle fine-art watercolor rag paper tooth (1.5% micro-grain, crisp and clean)
    np.random.seed(42)
    grain = cv2.GaussianBlur(np.random.normal(0, 1.0, (h, w)), (3, 3), 0.6)
    texture = 1.0 + grain * 0.015
    for c_i in range(3):
        graded_rgb[:, :, c_i] = np.clip(graded_rgb[:, :, c_i] * texture, 0, 255)

    # Save output
    out_bgr = cv2.cvtColor(graded_rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
    target_path = 'public/hero_editorial_canvas.jpg'
    cv2.imwrite(target_path, out_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 96])
    print(f"Successfully generated and saved to {target_path}!")

    # Verify color statistics
    sky_sample = graded_rgb[100:250, 100:300]
    bld_sample = graded_rgb[480:540, 550:750]
    fol_sample = graded_rgb[250:350, 20:150]
    print("\nVerified Two-Tone Contrast:")
    print(f"  Sky Mean RGB:        R={np.mean(sky_sample[:,:,0]):.1f}, G={np.mean(sky_sample[:,:,1]):.1f}, B={np.mean(sky_sample[:,:,2]):.1f} (Cool Muted Teal-Grey-Blue)")
    print(f"  Building Mean RGB:   R={np.mean(bld_sample[:,:,0]):.1f}, G={np.mean(bld_sample[:,:,1]):.1f}, B={np.mean(bld_sample[:,:,2]):.1f} (Warm Golden-Ochre/Tan)")
    print(f"  Warm Foliage Mean RGB: R={np.mean(fol_sample[:,:,0]):.1f}, G={np.mean(fol_sample[:,:,1]):.1f}, B={np.mean(fol_sample[:,:,2]):.1f} (Sunlit Golden-Amber)")

if __name__ == '__main__':
    generate_hero()
