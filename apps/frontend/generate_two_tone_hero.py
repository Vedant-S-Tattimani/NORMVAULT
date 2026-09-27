import cv2
import numpy as np

def generate_hero():
    ref_src = r'C:\Users\Lenovo\.gemini\antigravity-ide\brain\dc1bf6b2-4892-42aa-ac84-18350561f17e\clean_reference_artwork_1790524015071.jpg'
    base_src = r'C:\Users\Lenovo\.gemini\antigravity-ide\brain\dc1bf6b2-4892-42aa-ac84-18350561f17e\seamless_hero_artwork_1790526034280.jpg'
    
    ref = cv2.imread(ref_src)
    base = cv2.imread(base_src)
    h, w, c = base.shape
    print(f"Loaded source assets ({w}x{h}).")

    # =========================================================================
    # STEP 1: Restore authentic Indian Parliament (Sansad Bhavan) & Tiranga Flag
    # =========================================================================
    # Extract clean matte for flag and flagpole atop the dome
    flag_zone_ref = ref[425:485, 680:735]
    sky_ref_color = np.array([218.0, 240.0, 248.0])
    sky_dist = np.linalg.norm(flag_zone_ref.astype(float) - sky_ref_color, axis=2)
    flag_matte = np.clip((sky_dist - 18.0) / 22.0, 0, 1).astype(np.float32)
    flag_matte = cv2.GaussianBlur(flag_matte, (3, 3), 0.6)

    # Building mask for dome and sandstone colonnade
    building_mask = np.zeros((h, w), dtype=np.float32)
    building_mask[425:485, 680:735] = flag_matte

    # Central dome
    cv2.ellipse(building_mask, (693, 502), (32, 22), 0, 0, 360, 1.0, -1)

    # Colonnade body
    colonnade_pts = np.array([
        [505, 535], [520, 518], [610, 510], [690, 508], [770, 510], [860, 518], [875, 535],
        [875, 580], [505, 580]
    ], dtype=np.int32)
    cv2.fillPoly(building_mask, [colonnade_pts], 1.0)

    # Smooth colonnade boundaries for seamless integration with flanking trees
    b_mask_smooth = cv2.GaussianBlur(building_mask, (11, 11), 3.0)
    b_mask_smooth[425:485, 680:735] = np.maximum(b_mask_smooth[425:485, 680:735], flag_matte)

    # Composite authentic Sansad Bhavan and flag into canvas
    img = base.astype(np.float32) * (1.0 - b_mask_smooth[:, :, np.newaxis]) + ref.astype(np.float32) * b_mask_smooth[:, :, np.newaxis]
    img = np.clip(img, 0, 255).astype(np.uint8)
    print("Step 1: Successfully composited authentic Sansad Bhavan and Indian Tricolor Flag.")

    # =========================================================================
    # STEP 2: Clean bottom text/watermarks for multilingual overlay
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
    print("Step 2: Cleaned bottom corners for multilingual UI text.")

    # =========================================================================
    # STEP 3: Fully eliminate horizontal seam line across eyebrows
    # =========================================================================
    # 3a. Inpaint anomalous bright seam pixels along y=581..595
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

    # 3b. Sample natural foliage colors from canopy directly above
    foliage_palette = []
    for fy in range(550, 580, 2):
        for fx in range(500, 900, 3):
            bgr = img[fy, fx].astype(float)
            if np.mean(bgr) < 95:
                foliage_palette.append(bgr)
    foliage_palette = np.array(foliage_palette)

    # 3c. Paint cascading watercolor leaf clusters & botanical brushstrokes across x=515..885
    rng = np.random.RandomState(137)
    botanical = np.zeros((h, w, 4), dtype=np.float32)

    cur_x = 515.0
    x_coords = []
    while cur_x < 885.0:
        x_coords.append(cur_x)
        cur_x += rng.uniform(4.5, 9.5)

    for cx_f in x_coords:
        cx = int(cx_f)
        center_dist = abs(cx - 692)
        base_y = int(585 + 3.5 * np.sin(cx * 0.035) + rng.uniform(-1.5, 2.5))

        if center_dist < 35:
            max_drop = rng.uniform(8, 16)
        elif center_dist < 90:
            max_drop = rng.uniform(12, 22)
        else:
            max_drop = rng.uniform(10, 26)

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

    # 3d. Ambient contact shadow under leaves
    alpha_mask = botanical[:, :, 3]
    shadow_mask = cv2.GaussianBlur(alpha_mask, (15, 15), 5.0)
    shadow_mask = np.clip(shadow_mask * 0.42, 0, 0.42)

    img_float = img.astype(np.float32)
    for c_i in range(3):
        img_float[:, :, c_i] *= (1.0 - shadow_mask)

    bot_a = botanical[:, :, 3:4]
    bot_bgr = botanical[:, :, :3]
    blended = img_float * (1.0 - bot_a) + bot_bgr * bot_a
    img = np.clip(blended, 0, 255).astype(np.uint8)

    # 3e. Texture continuity glaze
    band = img[582:608, 490:910].copy()
    glaze = cv2.bilateralFilter(band, d=7, sigmaColor=28, sigmaSpace=7)
    img[582:608, 490:910] = cv2.addWeighted(band, 0.45, glaze, 0.55, 0)
    print("Step 3: Seamless botanical watercolor blending across eyebrows complete.")

    # =========================================================================
    # STEP 4: Restore Two-Tone Palette Contrast (Cool Teal vs Warm Golden-Ochre)
    # =========================================================================
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # Sky & Cool areas
    sky_mask = np.clip((H - 70) / 10.0, 0, 1) * np.clip((125 - H) / 10.0, 0, 1)
    H = np.where(sky_mask > 0, 93.0 + (H - 85.0) * 0.35, H)
    S = np.where(sky_mask > 0, np.clip(S * 1.05 + 8.0, 65, 130), S)

    # Foliage highlights, Parliament Building, and Warm Areas
    warm_mask = np.clip((H - 8) / 6.0, 0, 1) * np.clip((38 - H) / 8.0, 0, 1)
    H = np.where(warm_mask > 0, np.clip(H + 1.2, 14, 25), H)
    S = np.where(warm_mask > 0, np.clip(S * 1.08 + 8.0, 70, 185), S)

    # Clothing areas
    for y_cl in range(700, h):
        for x_cl in range(0, w):
            if (x_cl < 450 or x_cl > 950) and V[y_cl, x_cl] < 160:
                if H[y_cl, x_cl] > 35 and H[y_cl, x_cl] < 130:
                    H[y_cl, x_cl] = 90.0
                    S[y_cl, x_cl] = np.clip(S[y_cl, x_cl] * 1.1 + 5.0, 40, 120)

    hsv[:, :, 0] = np.clip(H, 0, 179)
    hsv[:, :, 1] = np.clip(S, 0, 255)
    hsv[:, :, 2] = np.clip(V, 0, 255)
    graded_rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

    # Split-toning
    lum = (0.299 * graded_rgb[:, :, 0] + 0.587 * graded_rgb[:, :, 1] + 0.114 * graded_rgb[:, :, 2]) / 255.0
    shadow_w = np.clip(1.0 - lum * 1.8, 0, 1)[:, :, np.newaxis]
    shadow_teal = np.array([-7.0, 3.0, 15.0], dtype=np.float32)
    graded_rgb = np.clip(graded_rgb + shadow_w * shadow_teal, 0, 255)

    highlight_w = np.clip((lum - 0.35) * 1.6, 0, 1)[:, :, np.newaxis]
    highlight_gold = np.array([12.0, 6.0, -10.0], dtype=np.float32)
    graded_rgb = np.clip(graded_rgb + highlight_w * highlight_gold, 0, 255)

    # Micro paper texture
    np.random.seed(42)
    grain = cv2.GaussianBlur(np.random.normal(0, 1.0, (h, w)), (3, 3), 0.6)
    texture = 1.0 + grain * 0.015
    for c_i in range(3):
        graded_rgb[:, :, c_i] = np.clip(graded_rgb[:, :, c_i] * texture, 0, 255)

    out_bgr = cv2.cvtColor(graded_rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
    target_path = 'public/hero_editorial_canvas.jpg'
    cv2.imwrite(target_path, out_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 96])
    print(f"Step 4: Saved final artwork to {target_path} successfully!")

if __name__ == '__main__':
    generate_hero()
