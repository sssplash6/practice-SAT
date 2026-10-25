"""hand_tall0.png (green screen, gemini-3-pro-image via OpenRouter) -> hand.png, keyed and despilled.
Prints the size and the marker tip that board.html's HAND constant needs."""
import numpy as np
from PIL import Image, ImageFilter
a = np.asarray(Image.open("hand_tall0.png").convert("RGB")).astype(float)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
alpha = np.clip(1 - (g - np.maximum(r, b) - 8) / 40, 0, 1)
g2 = np.minimum(g, (r + b) / 2 + 10)                       # pull the green spill toward a skin shadow tone
al = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
im = Image.fromarray(np.dstack([r, g2, b]).astype(np.uint8), "RGB").convert("RGBA")
im.putalpha(al)
ys, xs = np.nonzero(np.asarray(al) > 128)
im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
A = np.asarray(im)[..., 3]
ty, tx = np.nonzero(A > 128); i = tx.argmin()
print("size", im.size, "tip", int(tx[i]), int(ty[i]))
im.save("hand.png")
bg = Image.new("RGBA", im.size, (250, 250, 247, 255)); bg.alpha_composite(im); bg.convert("RGB").resize((im.size[0] // 2, im.size[1] // 2)).save("hand_check.jpg")
