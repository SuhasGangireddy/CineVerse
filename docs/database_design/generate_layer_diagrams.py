import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

BG = '#0d1117'
CARD_BG = '#161b22'
ENTITY = '#1f6feb'
BRIDGE = '#238636'
LOOKUP = '#6e7681'
TEXT = '#e6edf3'
PK = '#f0883e'
FK = '#a371f7'
ARROW = '#484f58'

def make_fig(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis('off')
    return fig, ax

def entity_box(ax, x, y, name, attrs, w=2.6, color=ENTITY):
    row_h = 0.32
    head_h = 0.45
    h = head_h + len(attrs) * row_h + 0.2

    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                           facecolor=CARD_BG, edgecolor=color, linewidth=2.2)
    ax.add_patch(rect)

    # header
    hdr = FancyBboxPatch((x, y + h - head_h), w, head_h,
                          boxstyle="round,pad=0.05", facecolor=color, edgecolor=color)
    ax.add_patch(hdr)
    ax.text(x + w/2, y + h - head_h/2, name, ha='center', va='center',
            fontsize=10, fontweight='bold', color='white', fontfamily='monospace')

    for i, (attr, kind) in enumerate(attrs):
        ay = y + h - head_h - 0.15 - (i + 0.5) * row_h
        if kind == 'pk':
            ax.text(x + 0.12, ay, 'PK', va='center', fontsize=7, color=PK,
                    fontweight='bold', fontfamily='monospace')
            ax.text(x + 0.55, ay, attr, va='center', fontsize=8, color=PK,
                    fontfamily='monospace', fontstyle='italic')
        elif kind == 'fk':
            ax.text(x + 0.12, ay, 'FK', va='center', fontsize=7, color=FK,
                    fontweight='bold', fontfamily='monospace')
            ax.text(x + 0.55, ay, attr, va='center', fontsize=8, color=FK,
                    fontfamily='monospace')
        elif kind == 'cpk':
            ax.text(x + 0.12, ay, 'PK', va='center', fontsize=7, color=PK,
                    fontweight='bold', fontfamily='monospace')
            ax.text(x + 0.55, ay, attr, va='center', fontsize=8, color=FK,
                    fontfamily='monospace', fontstyle='italic')
        else:
            ax.text(x + 0.15, ay, attr, va='center', fontsize=8, color='#c9d1d9',
                    fontfamily='monospace')

    center = (x + w/2, y + h/2)
    top = (x + w/2, y + h)
    bottom = (x + w/2, y)
    left = (x, y + h/2)
    right = (x + w, y + h/2)
    return {'center': center, 'top': top, 'bottom': bottom, 'left': left, 'right': right}

def rel_line(ax, p1, p2, label='', c1='1', c2='M'):
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='-', color=ARROW, lw=1.5))
    # cardinality labels
    dx, dy = p2[0]-p1[0], p2[1]-p1[1]
    ax.text(p1[0]+dx*0.15, p1[1]+dy*0.15+0.12, c1, ha='center', fontsize=8,
            color='#f85149', fontweight='bold', fontfamily='monospace')
    ax.text(p1[0]+dx*0.85, p1[1]+dy*0.85+0.12, c2, ha='center', fontsize=8,
            color='#f85149', fontweight='bold', fontfamily='monospace')
    if label:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        ax.text(mx, my-0.2, label, ha='center', fontsize=7, color='#8b949e',
                fontfamily='monospace',
                bbox=dict(facecolor=BG, edgecolor='none', pad=2))

OUT = 'docs/database_design'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIAGRAM 1: CORE — Movie, Person, Credits, Genre, Distributor
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig, ax = make_fig(18, 10)
ax.set_xlim(0, 18)
ax.set_ylim(0, 10)

ax.text(9, 9.6, 'Layer 1: Core — Movie Catalog & Credits', ha='center',
        fontsize=14, fontweight='bold', color='#58a6ff', fontfamily='sans-serif')

m = entity_box(ax, 7, 5.5, 'Movie', [
    ('movie_id', 'pk'), ('imdb_id  UNIQUE', ''), ('title  NOT NULL', ''),
    ('release_year', ''), ('runtime_minutes', ''), ('language', ''),
    ('budget / revenue', ''), ('imdb_rating', ''),
], w=3, color=ENTITY)

p = entity_box(ax, 0.5, 5, 'Person', [
    ('person_id', 'pk'), ('imdb_person_id', ''), ('name  NOT NULL', ''),
    ('birth_year', ''), ('death_year', ''), ('primary_profession', ''),
], w=2.8, color=ENTITY)

rt = entity_box(ax, 0.5, 1.5, 'RoleType', [
    ('role_type_id', 'pk'), ('role_name  UNIQUE', ''),
], w=2.8, color=LOOKUP)

mc = entity_box(ax, 4, 2, 'MovieCredit', [
    ('credit_id', 'pk'), ('movie_id', 'fk'), ('person_id', 'fk'),
    ('role_type_id', 'fk'), ('character_name', ''), ('billing_order', ''),
], w=3, color=BRIDGE)

g = entity_box(ax, 11.5, 7, 'Genre', [
    ('genre_id', 'pk'), ('genre_name  UNIQUE', ''),
], w=2.8, color=LOOKUP)

mg = entity_box(ax, 11.5, 5, 'MovieGenre', [
    ('movie_id', 'cpk'), ('genre_id', 'cpk'),
], w=2.8, color=BRIDGE)

d = entity_box(ax, 14.8, 3.5, 'Distributor', [
    ('distributor_id', 'pk'), ('name', ''), ('address', ''), ('country', ''),
], w=2.8, color=ENTITY)

md = entity_box(ax, 11.5, 2, 'MovieDistributor', [
    ('movie_id', 'cpk'), ('distributor_id', 'cpk'), ('region', ''),
], w=2.8, color=BRIDGE)

rel_line(ax, p['right'], mc['left'], c1='1', c2='M')
rel_line(ax, m['bottom'], mc['top'], c1='1', c2='M')
rel_line(ax, rt['right'], mc['left'], c1='1', c2='M')
rel_line(ax, m['right'], mg['left'], c1='1', c2='M')
rel_line(ax, g['bottom'], mg['top'], c1='1', c2='M')
rel_line(ax, m['right'], md['left'], c1='1', c2='M')
rel_line(ax, d['left'], md['right'], c1='1', c2='M')

plt.tight_layout()
plt.savefig(f'{OUT}/layer1_core.png', dpi=180, facecolor=BG, bbox_inches='tight')
plt.close()
print("Saved layer1_core.png")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIAGRAM 2: USERS — UserProfile, Rating, Review, ExternalRating
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig, ax = make_fig(16, 9)
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)

ax.text(8, 8.6, 'Layer 2: Users — Ratings & Reviews', ha='center',
        fontsize=14, fontweight='bold', color='#58a6ff', fontfamily='sans-serif')

mv = entity_box(ax, 6.5, 5, 'Movie', [
    ('movie_id', 'pk'), ('title', ''), ('imdb_rating', ''),
], w=2.8, color=ENTITY)

u = entity_box(ax, 0.5, 4.5, 'UserProfile', [
    ('user_id', 'pk'), ('username  UNIQUE', ''), ('email  UNIQUE', ''),
    ('age_group  CHECK', ''), ('preferred_language', ''),
], w=3, color=ENTITY)

ur = entity_box(ax, 4, 1, 'UserRating', [
    ('user_id', 'cpk'), ('movie_id', 'cpk'),
    ('rating  CHECK(0-10)', ''), ('rating_date', ''),
], w=3, color=BRIDGE)

rv = entity_box(ax, 0.5, 0.5, 'Review', [
    ('review_id', 'pk'), ('user_id', 'fk'), ('movie_id', 'fk'),
    ('review_text  NOT NULL', ''), ('sentiment', ''),
], w=3, color=ENTITY)

er = entity_box(ax, 10.5, 2, 'ExternalRating', [
    ('movie_id', 'cpk'), ('source_name', 'cpk'),
    ('score', ''), ('max_score', ''), ('vote_count', ''),
], w=3, color=BRIDGE)

rel_line(ax, u['right'], ur['left'], c1='1', c2='M')
rel_line(ax, mv['bottom'], ur['top'], c1='1', c2='M')
rel_line(ax, u['bottom'], rv['top'], c1='1', c2='M')
rel_line(ax, mv['bottom'], rv['top'], c1='1', c2='M')
rel_line(ax, mv['right'], er['left'], c1='1', c2='M')

plt.tight_layout()
plt.savefig(f'{OUT}/layer2_users.png', dpi=180, facecolor=BG, bbox_inches='tight')
plt.close()
print("Saved layer2_users.png")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIAGRAM 3: DISCOVERY — Tags, Recommendations, Streaming, Awards
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig, ax = make_fig(18, 11)
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)

ax.text(9, 10.6, 'Layer 3: Discovery — Tags, Streaming, Awards, Recommendations', ha='center',
        fontsize=14, fontweight='bold', color='#58a6ff', fontfamily='sans-serif')

mv = entity_box(ax, 0.5, 7, 'Movie', [
    ('movie_id', 'pk'), ('title', ''),
], w=2.5, color=ENTITY)

usr = entity_box(ax, 0.5, 3, 'UserProfile', [
    ('user_id', 'pk'), ('username', ''),
], w=2.5, color=ENTITY)

tg = entity_box(ax, 7, 8.5, 'Tag', [
    ('tag_id', 'pk'), ('tag_name  UNIQUE', ''),
], w=2.5, color=LOOKUP)

mtr = entity_box(ax, 4, 6.5, 'MovieTagRelevance', [
    ('movie_id', 'cpk'), ('tag_id', 'cpk'),
    ('relevance_score CHECK(0-1)', ''),
], w=3.5, color=BRIDGE)

upt = entity_box(ax, 4, 3.5, 'UserPreferenceTag', [
    ('user_id', 'cpk'), ('tag_id', 'cpk'),
    ('preference_weight', ''),
], w=3.2, color=BRIDGE)

rec = entity_box(ax, 4, 0.5, 'RecommendationLog', [
    ('recommendation_id', 'pk'), ('user_id', 'fk'), ('movie_id', 'fk'),
    ('score', ''), ('explanation  NOT NULL', ''),
], w=3.5, color=ENTITY)

sp = entity_box(ax, 11, 8.5, 'StreamingPlatform', [
    ('platform_id', 'pk'), ('name', ''), ('country', ''),
], w=2.8, color=ENTITY)

ma = entity_box(ax, 10.5, 5.5, 'MovieAvailability', [
    ('movie_id', 'cpk'), ('platform_id', 'cpk'),
    ('region', 'cpk'), ('access_type  CHECK', 'cpk'),
    ('start_date', ''), ('end_date', ''),
], w=3.2, color=BRIDGE)

aw = entity_box(ax, 14.5, 8.5, 'Award', [
    ('award_id', 'pk'), ('award_name', ''), ('category', ''),
], w=2.8, color=LOOKUP)

maw = entity_box(ax, 14.5, 5, 'MovieAward', [
    ('movie_award_id', 'pk'), ('movie_id', 'fk'), ('award_id', 'fk'),
    ('person_id  FK NULL', ''), ('award_year  CHECK', ''), ('result  CHECK', ''),
], w=3, color=BRIDGE)

pc = entity_box(ax, 14.5, 1.5, 'ProductionCompany', [
    ('company_id', 'pk'), ('name', ''), ('country', ''),
], w=2.8, color=ENTITY)

mpc = entity_box(ax, 10.5, 1.5, 'MovieProdCompany', [
    ('movie_id', 'cpk'), ('company_id', 'cpk'),
], w=3, color=BRIDGE)

rel_line(ax, mv['right'], mtr['left'], c1='1', c2='M')
rel_line(ax, tg['bottom'], mtr['top'], c1='1', c2='M')
rel_line(ax, usr['right'], upt['left'], c1='1', c2='M')
rel_line(ax, tg['bottom'], upt['right'], c1='1', c2='M')
rel_line(ax, usr['right'], rec['left'], c1='1', c2='M')
rel_line(ax, mv['bottom'], rec['left'], c1='1', c2='M')
rel_line(ax, mv['right'], ma['left'], c1='1', c2='M')
rel_line(ax, sp['bottom'], ma['top'], c1='1', c2='M')
rel_line(ax, aw['bottom'], maw['top'], c1='1', c2='M')
rel_line(ax, mv['right'], maw['left'], c1='1', c2='M')
rel_line(ax, pc['left'], mpc['right'], c1='1', c2='M')
rel_line(ax, mv['bottom'], mpc['left'], c1='1', c2='M')

plt.tight_layout()
plt.savefig(f'{OUT}/layer3_discovery.png', dpi=180, facecolor=BG, bbox_inches='tight')
plt.close()
print("Saved layer3_discovery.png")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIAGRAM 4: SOCIAL — Watchlist, WatchParty
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig, ax = make_fig(16, 9)
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)

ax.text(8, 8.6, 'Layer 4: Social — Watchlists & Group Watch', ha='center',
        fontsize=14, fontweight='bold', color='#58a6ff', fontfamily='sans-serif')

mv = entity_box(ax, 6.5, 5.5, 'Movie', [
    ('movie_id', 'pk'), ('title', ''),
], w=2.5, color=ENTITY)

usr = entity_box(ax, 0.5, 5.5, 'UserProfile', [
    ('user_id', 'pk'), ('username', ''),
], w=2.5, color=ENTITY)

wl = entity_box(ax, 0.5, 2, 'Watchlist', [
    ('watchlist_id', 'pk'), ('user_id', 'fk'), ('name', ''),
], w=2.8, color=ENTITY)

wli = entity_box(ax, 4.5, 2, 'WatchlistItem', [
    ('watchlist_id', 'cpk'), ('movie_id', 'cpk'),
    ('watched_status  CHECK', ''), ('added_at', ''),
], w=3.2, color=BRIDGE)

wp = entity_box(ax, 10, 5, 'WatchParty', [
    ('party_id', 'pk'), ('host_user_id', 'fk'),
    ('party_name', ''), ('planned_date', ''),
], w=3, color=ENTITY)

wpm = entity_box(ax, 13.2, 2.5, 'WatchPartyMember', [
    ('party_id', 'cpk'), ('user_id', 'cpk'),
], w=2.5, color=BRIDGE)

wps = entity_box(ax, 10, 0.5, 'WatchPartySuggestion', [
    ('party_id', 'cpk'), ('movie_id', 'cpk'),
    ('group_score', ''), ('suggested_by  FK', ''),
], w=3.2, color=BRIDGE)

rel_line(ax, usr['bottom'], wl['top'], c1='1', c2='M')
rel_line(ax, wl['right'], wli['left'], c1='1', c2='M')
rel_line(ax, mv['bottom'], wli['top'], c1='1', c2='M')
rel_line(ax, usr['right'], wp['left'], c1='1', c2='M')
rel_line(ax, wp['right'], wpm['left'], c1='1', c2='M')
rel_line(ax, wp['bottom'], wps['top'], c1='1', c2='M')
rel_line(ax, mv['bottom'], wps['left'], c1='1', c2='M')

plt.tight_layout()
plt.savefig(f'{OUT}/layer4_social.png', dpi=180, facecolor=BG, bbox_inches='tight')
plt.close()
print("Saved layer4_social.png")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIAGRAM 5: HIGH-LEVEL OVERVIEW (entities only, no attributes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

fig, ax = make_fig(20, 12)
ax.set_xlim(0, 20)
ax.set_ylim(0, 12)

ax.text(10, 11.5, 'CineVerse — High-Level Entity Overview', ha='center',
        fontsize=15, fontweight='bold', color='#58a6ff', fontfamily='sans-serif')
ax.text(10, 11.1, '14 Entities  +  13 Bridge Tables  =  27 Tables', ha='center',
        fontsize=9, color='#8b949e', fontfamily='sans-serif')

def oval(ax, x, y, name, color=ENTITY, w=2.2, h=0.7):
    from matplotlib.patches import Ellipse
    e = Ellipse((x, y), w, h, facecolor=CARD_BG, edgecolor=color, linewidth=2.2)
    ax.add_patch(e)
    ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold',
            color=color, fontfamily='sans-serif')
    return (x, y)

def diamond(ax, x, y, name, color=BRIDGE):
    s = 0.6
    pts = [(x, y+s), (x+s*1.5, y), (x, y-s), (x-s*1.5, y)]
    poly = plt.Polygon(pts, facecolor=CARD_BG, edgecolor=color, linewidth=1.8)
    ax.add_patch(poly)
    ax.text(x, y, name, ha='center', va='center', fontsize=6.5, color=color,
            fontfamily='monospace', fontweight='bold')
    return (x, y)

def simple_line(ax, p1, p2, c1='', c2=''):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=ARROW, lw=1.3, zorder=0)
    if c1:
        ax.text(p1[0]+(p2[0]-p1[0])*0.18, p1[1]+(p2[1]-p1[1])*0.18+0.18,
                c1, ha='center', fontsize=7, color='#f85149', fontweight='bold', fontfamily='monospace')
    if c2:
        ax.text(p1[0]+(p2[0]-p1[0])*0.82, p1[1]+(p2[1]-p1[1])*0.82+0.18,
                c2, ha='center', fontsize=7, color='#f85149', fontweight='bold', fontfamily='monospace')

# entities
e_movie = oval(ax, 10, 8.5, 'Movie', w=2.5, h=0.8)
e_person = oval(ax, 3, 9.5, 'Person')
e_genre = oval(ax, 14, 10, 'Genre', color=LOOKUP)
e_roletype = oval(ax, 1, 7.5, 'RoleType', color=LOOKUP)
e_dist = oval(ax, 17, 8.5, 'Distributor')
e_user = oval(ax, 3, 5.5, 'UserProfile')
e_tag = oval(ax, 10, 5.5, 'Tag', color=LOOKUP)
e_platform = oval(ax, 17, 5.5, 'StreamingPlatform')
e_award = oval(ax, 17, 2.5, 'Award', color=LOOKUP)
e_prodco = oval(ax, 14, 2.5, 'ProductionCo')
e_wl = oval(ax, 1, 3, 'Watchlist')
e_wp = oval(ax, 5.5, 1.5, 'WatchParty')
e_rec = oval(ax, 7, 3.5, 'RecLog')
e_review = oval(ax, 1, 1, 'Review')

# bridges
d_credit = diamond(ax, 5.5, 8.5, 'Credit')
d_mg = diamond(ax, 12.5, 9, 'M:G')
d_md = diamond(ax, 15, 7, 'M:D')
d_ur = diamond(ax, 5.5, 6.5, 'Rating')
d_mtr = diamond(ax, 10, 7, 'Tag\nScore')
d_upt = diamond(ax, 6.5, 5, 'Pref\nTag')
d_avail = diamond(ax, 14, 6, 'Avail')
d_maward = diamond(ax, 14, 4, 'M:Award')
d_mpc = diamond(ax, 12, 3, 'M:PC')
d_wli = diamond(ax, 3, 2, 'WL\nItem')
d_wpm = diamond(ax, 8, 1.5, 'Party\nMember')
d_wps = diamond(ax, 8, 0.3, 'Party\nSugg')

# connect
simple_line(ax, e_person, d_credit, '1', 'M')
simple_line(ax, e_movie, d_credit, '1', 'M')
simple_line(ax, e_movie, d_mg, '1', 'M')
simple_line(ax, e_genre, d_mg, '1', 'M')
simple_line(ax, e_movie, d_md, '1', 'M')
simple_line(ax, e_dist, d_md, '1', 'M')
simple_line(ax, e_user, d_ur, '1', 'M')
simple_line(ax, e_movie, d_ur, '1', 'M')
simple_line(ax, e_movie, d_mtr, '1', 'M')
simple_line(ax, e_tag, d_mtr, '1', 'M')
simple_line(ax, e_user, d_upt, '1', 'M')
simple_line(ax, e_tag, d_upt, '1', 'M')
simple_line(ax, e_movie, d_avail, '1', 'M')
simple_line(ax, e_platform, d_avail, '1', 'M')
simple_line(ax, e_movie, d_maward, '1', 'M')
simple_line(ax, e_award, d_maward, '1', 'M')
simple_line(ax, e_movie, d_mpc, '1', 'M')
simple_line(ax, e_prodco, d_mpc, '1', 'M')
simple_line(ax, e_user, e_wl, '1', 'M')
simple_line(ax, e_wl, d_wli, '1', 'M')
simple_line(ax, e_user, e_wp, '1', 'M')
simple_line(ax, e_wp, d_wpm, '1', 'M')
simple_line(ax, e_wp, d_wps, '1', 'M')
simple_line(ax, e_user, e_rec, '1', 'M')
simple_line(ax, e_user, e_review, '1', 'M')

# legend
ax.add_patch(plt.Circle((16.5, 0.9), 0.15, facecolor=ENTITY, edgecolor=ENTITY))
ax.text(16.85, 0.9, 'Entity', va='center', fontsize=8, color=TEXT, fontfamily='sans-serif')
ax.add_patch(plt.Circle((16.5, 0.4), 0.15, facecolor=LOOKUP, edgecolor=LOOKUP))
ax.text(16.85, 0.4, 'Lookup', va='center', fontsize=8, color=TEXT, fontfamily='sans-serif')
pts_d = [(18.5, 0.3), (18.8, 0.15), (18.5, 0), (18.2, 0.15)]
ax.add_patch(plt.Polygon(pts_d, facecolor=BRIDGE, edgecolor=BRIDGE))
ax.text(19, 0.15, 'Bridge (M:N)', va='center', fontsize=8, color=TEXT, fontfamily='sans-serif')

plt.tight_layout()
plt.savefig(f'{OUT}/overview_high_level.png', dpi=180, facecolor=BG, bbox_inches='tight')
plt.close()
print("Saved overview_high_level.png")

print("\nAll 5 diagrams generated.")
