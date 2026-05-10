#!/usr/bin/env python3
"""Generate all icon and image assets for the PWA."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

OUT = "/home/claude/apinepa/assets"
os.makedirs(OUT, exist_ok=True)

# Brand palette
BG = (10, 10, 15)         # near-black
BG2 = (24, 26, 36)        # surface
AMBER = (255, 180, 0)     # primary accent
AMBER_BR = (255, 210, 70) # brighter
BLUE = (0, 122, 255)      # iOS system blue
WHITE = (245, 246, 250)
MUTED = (140, 145, 160)

def find_font(candidates, size):
  for path in candidates:
    if os.path.exists(path):
      try:
        return ImageFont.truetype(path, size)
      except Exception:
        pass
  return ImageFont.load_default()

BOLD_FONTS = [
  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
REG_FONTS = [
  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
  "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
MONO_FONTS = [
  "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
  "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
]

def rounded_rect_mask(size, radius):
  mask = Image.new("L", size, 0)
  d = ImageDraw.Draw(mask)
  d.rounded_rectangle((0, 0, size[0]-1, size[1]-1), radius=radius, fill=255)
  return mask

def make_icon(size, maskable=False):
  """Create a square PWA icon at the given size.
  If maskable, keep mark within ~80% inner safe zone."""
  pad = int(size * 0.10) if maskable else 0
  img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
  draw = ImageDraw.Draw(img)

  # Background — vertical gradient charcoal → near-black with subtle amber glow
  bg_layer = Image.new("RGB", (size, size), BG)
  bg_draw = ImageDraw.Draw(bg_layer)
  for y in range(size):
    t = y / max(1, size - 1)
    r = int(BG2[0] * (1 - t) + BG[0] * t)
    g = int(BG2[1] * (1 - t) + BG[1] * t)
    b = int(BG2[2] * (1 - t) + BG[2] * t)
    bg_draw.line([(0, y), (size, y)], fill=(r, g, b))

  # Soft amber radial glow in upper-left
  glow = Image.new("RGB", (size, size), (0, 0, 0))
  gd = ImageDraw.Draw(glow)
  gx, gy, gr = int(size * 0.32), int(size * 0.34), int(size * 0.55)
  for r in range(gr, 0, -2):
    alpha = int(120 * (1 - r / gr))
    gd.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(alpha, int(alpha*0.7), 0))
  glow = glow.filter(ImageFilter.GaussianBlur(size * 0.06))
  bg_layer = Image.blend(bg_layer, Image.eval(glow, lambda v: min(255, v + 0)), 0.45)

  # Round the background corners (iOS squircle-ish)
  radius = int(size * (0.225 if not maskable else 0.5))
  mask = rounded_rect_mask((size, size), radius)
  rounded = Image.new("RGBA", (size, size), (0, 0, 0, 0))
  rounded.paste(bg_layer, (0, 0), mask)

  d = ImageDraw.Draw(rounded)

  # Mark: stylized "{·}" with "API" wordmark below
  brace_font = find_font(MONO_FONTS, int((size - 2*pad) * 0.55))
  api_font = find_font(BOLD_FONTS, int((size - 2*pad) * 0.20))

  cx = size // 2
  cy = int(size * 0.45) + (pad // 2 if maskable else 0)

  # Brace pair "{ }" centered with a dot in the middle
  brace_text = "{ }"
  bbox = d.textbbox((0, 0), brace_text, font=brace_font)
  bw = bbox[2] - bbox[0]
  bh = bbox[3] - bbox[1]
  bx = cx - bw // 2
  by = cy - bh // 2 - bbox[1]
  d.text((bx, by), brace_text, font=brace_font, fill=AMBER_BR)

  # Center dot
  dot_r = max(2, int(size * 0.035))
  d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=BLUE)

  # Wordmark
  api_text = "API"
  abox = d.textbbox((0, 0), api_text, font=api_font)
  aw = abox[2] - abox[0]
  ay = int(size * 0.74) - (pad // 2 if maskable else 0)
  d.text((cx - aw // 2, ay), api_text, font=api_font, fill=WHITE)

  # Tiny "NEPA-PRO" sublabel for larger icons
  if size >= 256:
    sub_font = find_font(BOLD_FONTS, int(size * 0.058))
    sub = "NEPA-PRO"
    sbbox = d.textbbox((0, 0), sub, font=sub_font)
    sw = sbbox[2] - sbbox[0]
    sy = int(size * 0.86) - (pad // 2 if maskable else 0)
    d.text((cx - sw // 2, sy), sub, font=sub_font, fill=AMBER)

  return rounded

# Generate PWA icons
for s in [192, 256, 384, 512]:
  icon = make_icon(s, maskable=False)
  icon.save(f"{OUT}/icon-{s}.png", optimize=True)
  print(f"  → icon-{s}.png")

# Maskable variant
mask_icon = make_icon(512, maskable=True)
mask_icon.save(f"{OUT}/icon-maskable-512.png", optimize=True)
print(f"  → icon-maskable-512.png")

# Apple touch icon (180x180, no rounding — iOS rounds it)
apple = make_icon(180, maskable=False)
# Re-render flat (iOS adds its own rounding)
apple_flat = Image.new("RGB", (180, 180), BG)
adraw = ImageDraw.Draw(apple_flat)
# Fill with gradient again (without rounded corners)
for y in range(180):
  t = y / 179
  r = int(BG2[0] * (1 - t) + BG[0] * t)
  g = int(BG2[1] * (1 - t) + BG[1] * t)
  b = int(BG2[2] * (1 - t) + BG[2] * t)
  adraw.line([(0, y), (180, y)], fill=(r, g, b))
brace_f = find_font(MONO_FONTS, int(180 * 0.55))
api_f = find_font(BOLD_FONTS, int(180 * 0.20))
sub_f = find_font(BOLD_FONTS, int(180 * 0.07))
cx, cy = 90, int(180 * 0.45)
bt = "{ }"
bb = adraw.textbbox((0, 0), bt, font=brace_f)
bw = bb[2] - bb[0]
bh = bb[3] - bb[1]
adraw.text((cx - bw // 2, cy - bh // 2 - bb[1]), bt, font=brace_f, fill=AMBER_BR)
dot_r = 6
adraw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=BLUE)
at = "API"
ab = adraw.textbbox((0, 0), at, font=api_f)
aw = ab[2] - ab[0]
adraw.text((cx - aw // 2, int(180 * 0.72)), at, font=api_f, fill=WHITE)
sub = "NEPA-PRO"
sb = adraw.textbbox((0, 0), sub, font=sub_f)
sw = sb[2] - sb[0]
adraw.text((cx - sw // 2, int(180 * 0.86)), sub, font=sub_f, fill=AMBER)
apple_flat.save(f"{OUT}/apple-touch-icon.png", optimize=True)
print(f"  → apple-touch-icon.png")

# Favicon — 32x32 simplified
fav = Image.new("RGB", (64, 64), BG)
fd = ImageDraw.Draw(fav)
for y in range(64):
  t = y / 63
  r = int(BG2[0] * (1 - t) + BG[0] * t)
  g = int(BG2[1] * (1 - t) + BG[1] * t)
  b = int(BG2[2] * (1 - t) + BG[2] * t)
  fd.line([(0, y), (64, y)], fill=(r, g, b))
ff = find_font(MONO_FONTS, 44)
ft = "{ }"
fb = fd.textbbox((0, 0), ft, font=ff)
fw = fb[2] - fb[0]; fh = fb[3] - fb[1]
fd.text((32 - fw // 2, 32 - fh // 2 - fb[1]), ft, font=ff, fill=AMBER_BR)
fd.ellipse([29, 29, 35, 35], fill=BLUE)
fav.save(f"{OUT}/favicon-64.png", optimize=True)
# also 32
fav.resize((32, 32), Image.LANCZOS).save(f"{OUT}/favicon-32.png", optimize=True)
fav.resize((16, 16), Image.LANCZOS).save(f"{OUT}/favicon-16.png", optimize=True)
print(f"  → favicon-{16,32,64}.png")

# ----- OG Share Card (1200 × 630) — "life share / business card" -----
W, H = 1200, 630
og = Image.new("RGB", (W, H), BG)
od = ImageDraw.Draw(og)

# Background — diagonal gradient
for y in range(H):
  for x in range(0, W, 4):
    t = (x + y) / (W + H)
    r = int(BG2[0] * (1 - t) + BG[0] * t)
    g = int(BG2[1] * (1 - t) + BG[1] * t)
    b = int(BG2[2] * (1 - t) + BG[2] * t)
    od.line([(x, y), (x + 4, y)], fill=(r, g, b))

# Soft amber glow upper-left
glow = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
for r in range(360, 0, -3):
  a = int(180 * (1 - r / 360))
  gd.ellipse([200 - r, 150 - r, 200 + r, 150 + r], fill=(a, int(a * 0.7), 0))
glow = glow.filter(ImageFilter.GaussianBlur(40))
og = Image.blend(og, Image.eval(glow, lambda v: min(255, v)), 0.45)
od = ImageDraw.Draw(og)

# Subtle grid lines (technical / API feel)
for x in range(0, W, 60):
  od.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)
for y in range(0, H, 60):
  od.line([(0, y), (W, y)], fill=(255, 255, 255, 8), width=1)

# Top-left badge: small icon
badge = make_icon(120, maskable=False).convert("RGBA")
og.paste(badge, (60, 60), badge)

# Brand label
brand_f = find_font(BOLD_FONTS, 28)
od.text((200, 70), "API.NEPA-PRO.COM", font=brand_f, fill=AMBER)
sub_f = find_font(REG_FONTS, 20)
od.text((200, 110), "The Open Source API Directory · Free Tier · No Gatekeepers", font=sub_f, fill=MUTED)

# Headline (display)
head_f = find_font(BOLD_FONTS, 72)
od.text((60, 230), "805 free APIs.", font=head_f, fill=WHITE)
od.text((60, 320), "51 categories.", font=head_f, fill=WHITE)
od.text((60, 410), "Built for builders.", font=head_f, fill=AMBER_BR)

# Stats row
stat_label_f = find_font(REG_FONTS, 18)
stat_val_f = find_font(BOLD_FONTS, 36)

stats = [
  ("805", "APIs Indexed"),
  ("51", "Categories"),
  ("100%", "Free Tier"),
  ("PWA", "Install on iOS"),
]
sx = 60
for val, lbl in stats:
  od.text((sx, 525), val, font=stat_val_f, fill=AMBER_BR)
  vbox = od.textbbox((0, 0), val, font=stat_val_f)
  vw = vbox[2] - vbox[0]
  od.text((sx, 575), lbl, font=stat_label_f, fill=MUTED)
  lbox = od.textbbox((0, 0), lbl, font=stat_label_f)
  lw = lbox[2] - lbox[0]
  sx += max(vw, lw) + 64

# Right side: "business card" style block
card_x, card_y, card_w, card_h = 770, 200, 380, 360
card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
co = ImageDraw.Draw(card_overlay)
co.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=24,
                     fill=(255, 255, 255, 14), outline=(255, 180, 0, 100), width=2)
og = Image.alpha_composite(og.convert("RGBA"), card_overlay).convert("RGB")
od = ImageDraw.Draw(og)

# Card content
name_f = find_font(BOLD_FONTS, 30)
role_f = find_font(REG_FONTS, 18)
mono_f = find_font(MONO_FONTS, 14)
od.text((card_x + 28, card_y + 28), "NEPA-PRO", font=name_f, fill=WHITE)
od.text((card_x + 28, card_y + 64), "Operations · Construction · Solar", font=role_f, fill=MUTED)
od.line([(card_x + 28, card_y + 100), (card_x + card_w - 28, card_y + 100)],
        fill=(255, 180, 0, 200), width=1)

card_label_f = find_font(BOLD_FONTS, 12)
card_val_f = find_font(REG_FONTS, 16)

rows = [
  ("WEB", "nepa-pro.com"),
  ("API", "api.nepa-pro.com"),
  ("SISTER", "solarmason.com"),
  ("REGION", "Northeast PA · NEPA"),
  ("STATUS", "Veteran Owned · Active"),
]
ry = card_y + 120
for lbl, val in rows:
  od.text((card_x + 28, ry), lbl, font=card_label_f, fill=AMBER)
  od.text((card_x + 28, ry + 16), val, font=card_val_f, fill=WHITE)
  ry += 48

og.save(f"{OUT}/og-card.png", optimize=True)
print(f"  → og-card.png (1200×630)")

# Twitter card variant (same image, but ensure it's saved as twitter-card too)
og.save(f"{OUT}/twitter-card.png", optimize=True)

print("All assets generated.")
