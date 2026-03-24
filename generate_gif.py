from PIL import Image, ImageDraw, ImageFont
import math, random
import os

W, H = 800, 300
BG      = (245, 240, 232)  # Anthropic warm cream
FG_MAIN = (28,  25,  23)   # near-black brown
FG_SUB  = (120, 113, 108)  # muted warm gray
ACCENT  = (180,  75,  40)  # deeper coral/burnt sienna
FPS = 30
PAUSE_FRAMES = 45  # 1.5s pause when fully typed

screens = [
    ("Hey there!", "My name is Mashiur."),
    ("CS & Mathematics Major", "at Vanderbilt University."),
    ("Building voice AI agents", "for scheduling."),
    ("Building cyber range infrastructure", "that bridges theory and detection engineering."),
    ("I just like building and shipping", "things that work."),
    ("I work across the stack.", "I pick up whatever the problem needs."),
    ("Want to chat? Book a time", "khanflow.com/mashiur"),
]

VOICE_SCREEN_INDEX  = None  # wave on all screens
CYBER_SCREEN_INDEX  = 3     # scanning bar on cyber screen
BUILD_SCREEN_INDEX  = 4     # stacking blocks on build screen
STACK_SCREEN_INDEX  = 5     # vertical bars on stack screen
CSMATH_SCREEN_INDEX = 1     # algo graph on CS/Math screen
BOOK_SCREEN_INDEX   = 6     # khanflow logo on booking screen

def draw_khanflow_logo(d, scale=1.0):
    """Draw Khanflow logo: red dot, yellow dot, green dot, gray pill, 'Khanflow' text."""
    font_logo = get_font(int(22 * scale))
    dot_r   = int(7 * scale)
    pill_w  = int(24 * scale)
    pill_h  = int(14 * scale)
    gap     = int(10 * scale)

    # total width of logo elements
    total_w = (dot_r*2)*3 + pill_w + gap*3
    bbox = d.textbbox((0,0), "Khanflow", font=font_logo)
    text_w = bbox[2] - bbox[0]
    total_w += int(10 * scale) + text_w

    lx = (W - total_w) // 2
    cy = int(H - 38 * scale)

    # red dot  — bg-red-500   #ef4444
    d.ellipse([lx, cy-dot_r, lx+dot_r*2, cy+dot_r], fill=(239, 68, 68))
    lx += dot_r*2 + gap
    # yellow dot — bg-yellow-500 #eab308
    d.ellipse([lx, cy-dot_r, lx+dot_r*2, cy+dot_r], fill=(234, 179, 8))
    lx += dot_r*2 + gap
    # green dot  — bg-green-500  #22c55e
    d.ellipse([lx, cy-dot_r, lx+dot_r*2, cy+dot_r], fill=(34, 197, 94))
    lx += dot_r*2 + gap
    # gray pill  — bg-gray-400   #9ca3af
    d.rounded_rectangle([lx, cy-pill_h//2, lx+pill_w, cy+pill_h//2], radius=9999, fill=(156, 163, 175))
    lx += pill_w + int(10 * scale)
    # "Khanflow" text
    d.text((lx, cy - (bbox[3]-bbox[1])//2), "Khanflow", font=font_logo, fill=(28, 25, 23))

BAR_LABELS = ["UI", "API", "DB", "Cache", "Infra"]
BAR_COLORS = [(129,140,248),(104,211,145),(246,200,68),(229,62,62),(180,75,40)]

def draw_vbars(d, t):
    font_label = get_font(13)
    bw, gap = 48, 20
    total_w = len(BAR_LABELS) * bw + (len(BAR_LABELS)-1) * gap
    bx = (W - total_w) // 2
    max_bh = 65
    base_y = 268
    for i, (label, color) in enumerate(zip(BAR_LABELS, BAR_COLORS)):
        x = bx + i * (bw + gap)
        phase = math.sin(t * 2.5 + i * 0.9)
        bh = int(max_bh * (0.3 + 0.7 * (0.5 + 0.5 * phase)))
        d.rounded_rectangle([x, base_y-bh, x+bw, base_y], radius=5, fill=color)
        bbox = d.textbbox((0,0), label, font=font_label)
        lx = x + (bw - (bbox[2]-bbox[0])) // 2
        d.text((lx, base_y+3), label, font=font_label, fill=FG_SUB)

BLOCK_COLORS = [
    (229, 62,  62),
    (246, 200, 68),
    (104, 211, 145),
    (180, 75,  40),
    (203, 213, 224),
    (129, 140, 248),
]

def draw_blocks(d, t, total_duration):
    bw, bh, gap = 44, 22, 6
    cols, max_rows = 6, 3
    total_w = cols * bw + (cols-1) * gap
    base_x = (W - total_w) // 2
    base_y = 285
    total_blocks = cols * max_rows
    blocks_shown = int((t / total_duration) * total_blocks)
    for idx in range(min(blocks_shown, total_blocks)):
        row = idx // cols
        col = idx % cols
        x = base_x + col * (bw + gap)
        y = base_y - row * (bh + gap)
        color = BLOCK_COLORS[col % len(BLOCK_COLORS)]
        d.rounded_rectangle([x, y-bh, x+bw, y], radius=4, fill=color)

# Wave bar config matching the React component
WAVE_BARS = [
    {"color": (239, 68,  68),  "delay": 0.00, "max_h": 40, "w": 7},   # red-500
    {"color": (239, 68,  68),  "delay": 0.08, "max_h": 30, "w": 7},
    {"color": (234, 179,  8),  "delay": 0.16, "max_h": 44, "w": 7},   # yellow-500
    {"color": (234, 179,  8),  "delay": 0.24, "max_h": 34, "w": 7},
    {"color": (34,  197, 94),  "delay": 0.32, "max_h": 42, "w": 7},   # green-500
    {"color": (34,  197, 94),  "delay": 0.40, "max_h": 32, "w": 7},
    {"color": (156, 163, 175), "delay": 0.48, "max_h": 24, "w": 16},  # gray-400 pill
]

def get_font(size):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

font_main = get_font(42)
font_sub  = get_font(28)

frames = []
durations = []

def draw_wave(d, t, cx, cy, scale=1.0):
    """Draw animated wave bars centered at (cx, cy) at time t (seconds)."""
    duration = 0.6  # active mode
    bar_gap = int(12 * scale)
    min_h = int(7 * scale)

    # compute total width to center
    total_w = sum(int(b["w"] * scale) for b in WAVE_BARS) + bar_gap * (len(WAVE_BARS) - 1)
    x = cx - total_w // 2

    for bar in WAVE_BARS:
        bw = int(bar["w"] * scale)
        max_h = int(bar["max_h"] * scale)
        # sine wave: 0->1->0 over duration, offset by delay
        phase = ((t - bar["delay"]) % duration) / duration
        height = min_h + (max_h - min_h) * (0.5 - 0.5 * math.cos(phase * 2 * math.pi))
        height = max(min_h, int(height))
        top = cy - height // 2
        bot = cy + height // 2
        d.rounded_rectangle([x, top, x + bw, bot], radius=9999, fill=bar["color"])
        x += bw + bar_gap

GREEN = (80, 200, 120)

# Algo graph for CS/Math screen
random.seed(21)
G_NODES  = [(int(80  + i * (W-160) / 8), random.randint(155, 265)) for i in range(9)]
G_EDGES  = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(0,3),(2,5),(1,4),(4,7),(3,6)]
G_LABELS = ["sort","search","graph","DP","hash","tree","BFS","DFS","∑O(n)"]
G_COLORS = [ACCENT,GREEN,(129,140,248),(246,200,68),(104,211,145),
            (229,62,62),ACCENT,GREEN,FG_SUB]

def draw_algo_graph(d, t):
    font_node = get_font(12)
    progress  = min(1.0, t / 3.0)
    nodes_shown = int(progress * len(G_NODES)) + 1
    for a, b in G_EDGES:
        if a < nodes_shown and b < nodes_shown:
            pulse = 0.4 + 0.3 * math.sin(t * 2 + a)
            c = int(180 * pulse)
            d.line([G_NODES[a], G_NODES[b]], fill=(c, c, c-20), width=1)
    for i in range(min(nodes_shown, len(G_NODES))):
        nx, ny = G_NODES[i]
        color = G_COLORS[i]
        is_math = (i == len(G_NODES) - 1)
        r = 6 if not is_math else 4
        d.ellipse([nx-r, ny-r, nx+r, ny+r], fill=color)
        label = G_LABELS[i]
        bbox = d.textbbox((0,0), label, font=font_node)
        lx = nx - (bbox[2]-bbox[0])//2
        ly = ny - 18
        d.text((lx, ly), label, font=font_node, fill=FG_SUB if is_math else (28,25,23))

def draw_scan(img, d, t, total_duration):
    """Full-frame scanning bar that sweeps top to bottom repeatedly."""
    scan_period = 1.8  # seconds per sweep
    progress = (t % scan_period) / scan_period
    y = int(progress * H)

    # glow layers
    for offset, opacity in [(6, 15), (4, 30), (2, 60), (0, 180)]:
        shade = tuple(int(c * opacity / 255) + int(BG[i] * (1 - opacity/255)) for i, c in enumerate(GREEN))
        if 0 <= y - offset < H:
            d.line([(0, y - offset), (W, y - offset)], fill=shade, width=1)
    # bright scan line
    d.line([(0, y), (W, y)], fill=GREEN, width=2)

    # corner brackets on full frame
    bl = 22
    for (sx, sy, ex, ey) in [
        (0, 0, bl, 0), (0, 0, 0, bl),
        (W-bl, 0, W, 0), (W, 0, W, bl),
        (0, H-bl, 0, H), (0, H, bl, H),
        (W-bl, H, W, H), (W, H-bl, W, H),
    ]:
        d.line([(sx, sy), (ex, ey)], fill=GREEN, width=2)

def make_frame(top, bot, wave_t=None, scan_t=None, block_t=None, block_total=1, vbar_t=None, graph_t=None, show_logo=False):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text_y_top = H // 2 - 60
    text_y_bot = H // 2 + 10

    if scan_t is not None:
        draw_scan(img, d, scan_t, total_duration=1.8)

    if block_t is not None:
        draw_blocks(d, block_t, block_total)

    if vbar_t is not None:
        draw_vbars(d, vbar_t)

    if graph_t is not None:
        draw_algo_graph(d, graph_t)

    if show_logo:
        draw_khanflow_logo(d)

    if wave_t is not None:
        # shift text up, draw wave below
        text_y_top = H // 2 - 90
        text_y_bot = H // 2 - 30
        draw_wave(d, wave_t, cx=W // 2, cy=H // 2 + 55, scale=1.0)

    bbox = d.textbbox((0, 0), top, font=font_main)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, text_y_top), top, font=font_main, fill=ACCENT)

    if bot:
        bbox2 = d.textbbox((0, 0), bot, font=font_sub)
        bw = bbox2[2] - bbox2[0]
        d.text(((W - bw) // 2, text_y_bot), bot, font=font_sub, fill=FG_SUB)

    return img

for screen_idx, (top_full, bot_full) in enumerate(screens):
    is_cyber  = screen_idx == CYBER_SCREEN_INDEX
    is_build  = screen_idx == BUILD_SCREEN_INDEX
    is_stack  = screen_idx == STACK_SCREEN_INDEX
    is_csmath = screen_idx == CSMATH_SCREEN_INDEX
    is_book   = screen_idx == BOOK_SCREEN_INDEX
    max_len = max(len(top_full), len(bot_full))
    frame_count = [0]

    def next_t():
        t = frame_count[0] / FPS
        frame_count[0] += 1
        return t

    total_frames = max_len + PAUSE_FRAMES + max_len
    total_dur = total_frames / FPS

    # Type in
    for i in range(1, max_len + 1):
        top = top_full[:i] if i <= len(top_full) else top_full
        bot = bot_full[:i] if i <= len(bot_full) else bot_full
        t = next_t()
        frames.append(make_frame(top, bot,
            wave_t=None if (is_cyber or is_build or is_stack or is_csmath or is_book) else t,
            scan_t=t if is_cyber else None,
            block_t=t if is_build else None,
            block_total=total_dur,
            vbar_t=t if is_stack else None,
            graph_t=t if is_csmath else None,
            show_logo=is_book))
        durations.append(1000 // FPS)

    # Pause (hold for 1.5s = 45 frames)
    for _ in range(PAUSE_FRAMES):
        t = next_t()
        frames.append(make_frame(top_full, bot_full,
            wave_t=None if (is_cyber or is_build or is_stack or is_csmath or is_book) else t,
            scan_t=t if is_cyber else None,
            block_t=t if is_build else None,
            block_total=total_dur,
            vbar_t=t if is_stack else None,
            graph_t=t if is_csmath else None,
            show_logo=is_book))
        durations.append(1000 // FPS)

    # Delete
    for i in range(max_len, 0, -1):
        top = top_full[:i] if i <= len(top_full) else top_full
        bot = bot_full[:i] if i <= len(bot_full) else bot_full
        t = next_t()
        frames.append(make_frame(top, bot,
            wave_t=None if (is_cyber or is_build or is_stack or is_csmath or is_book) else t,
            scan_t=t if is_cyber else None,
            block_t=t if is_build else None,
            block_total=total_dur,
            vbar_t=t if is_stack else None,
            graph_t=t if is_csmath else None,
            show_logo=is_book))
        durations.append(1000 // FPS)

    # Blank frame between screens
    frames.append(Image.new("RGB", (W, H), BG))
    durations.append(1000 // FPS)

out = "/Users/md.mashiurrahmankhan/Downloads/MasonSlover/profile.gif"
frames[0].save(
    out,
    save_all=True,
    append_images=frames[1:],
    loop=0,
    duration=durations,
    optimize=False,
)
print(f"Done! Saved to {out} ({len(frames)} frames)")
