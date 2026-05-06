import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(28, 20))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')
ax.set_xlim(0, 28)
ax.set_ylim(0, 20)
ax.axis('off')

# colors
ENTITY_COLOR = '#1f6feb'
BRIDGE_COLOR = '#238636'
WEAK_COLOR = '#8b949e'
TEXT_COLOR = '#e6edf3'
ATTR_COLOR = '#c9d1d9'
LINE_COLOR = '#484f58'
PK_COLOR = '#f0883e'
TITLE_COLOR = '#58a6ff'

def draw_entity(x, y, name, attrs, w=3.2, h=None, color=ENTITY_COLOR, pk_attrs=None):
    if pk_attrs is None:
        pk_attrs = []
    if h is None:
        h = 0.55 + len(attrs) * 0.28

    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.1",
                           facecolor='#161b22', edgecolor=color, linewidth=2)
    ax.add_patch(rect)

    # header bar
    header_h = 0.45
    header = FancyBboxPatch((x - w/2, y + h/2 - header_h), w, header_h,
                             boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor=color, linewidth=0)
    ax.add_patch(header)

    ax.text(x, y + h/2 - header_h/2, name, ha='center', va='center',
            fontsize=9, fontweight='bold', color='white', fontfamily='monospace')

    for i, attr in enumerate(attrs):
        ay = y + h/2 - header_h - 0.18 - i * 0.28
        is_pk = attr in pk_attrs or attr.endswith(' PK')
        display = attr.replace(' PK', '').replace(' FK', '')
        prefix = ''
        if attr.endswith(' PK'):
            prefix = 'PK '
            display = attr.replace(' PK', '')
        elif attr.endswith(' FK'):
            prefix = 'FK '
            display = attr.replace(' FK', '')

        if prefix == 'PK ':
            ax.text(x - w/2 + 0.15, ay, f"{prefix}", ha='left', va='center',
                    fontsize=6.5, color=PK_COLOR, fontweight='bold', fontfamily='monospace')
            ax.text(x - w/2 + 0.55, ay, display, ha='left', va='center',
                    fontsize=7, color=PK_COLOR, fontfamily='monospace', style='italic')
        elif prefix == 'FK ':
            ax.text(x - w/2 + 0.15, ay, f"{prefix}", ha='left', va='center',
                    fontsize=6.5, color='#a371f7', fontweight='bold', fontfamily='monospace')
            ax.text(x - w/2 + 0.55, ay, display, ha='left', va='center',
                    fontsize=7, color='#a371f7', fontfamily='monospace')
        else:
            ax.text(x - w/2 + 0.15, ay, display, ha='left', va='center',
                    fontsize=7, color=ATTR_COLOR, fontfamily='monospace')

    return (x, y)

def draw_relation_line(p1, p2, label='', card1='', card2='', color=LINE_COLOR):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=1.2, zorder=0)
    if label:
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        ax.text(mx, my + 0.15, label, ha='center', va='bottom',
                fontsize=6, color='#8b949e', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#0d1117', edgecolor='none'))
    if card1:
        ax.text(p1[0] + (p2[0]-p1[0])*0.12, p1[1] + (p2[1]-p1[1])*0.12 + 0.15,
                card1, ha='center', va='bottom', fontsize=6.5, color='#f85149',
                fontweight='bold', fontfamily='monospace')
    if card2:
        ax.text(p1[0] + (p2[0]-p1[0])*0.88, p1[1] + (p2[1]-p1[1])*0.88 + 0.15,
                card2, ha='center', va='bottom', fontsize=6.5, color='#f85149',
                fontweight='bold', fontfamily='monospace')

# title
ax.text(14, 19.5, 'CineVerse — Entity-Relationship Diagram', ha='center', va='center',
        fontsize=18, fontweight='bold', color=TITLE_COLOR, fontfamily='sans-serif')
ax.text(14, 19.1, '27 Tables  |  ISE 503 Data Management  |  Spring 2026', ha='center', va='center',
        fontsize=9, color='#8b949e', fontfamily='sans-serif')

# === CORE LAYER (top) ===

p_movie = draw_entity(8, 16, 'Movie', [
    'movie_id PK', 'imdb_id (UNIQUE)', 'title', 'release_year',
    'runtime_minutes', 'language', 'budget', 'revenue',
    'imdb_rating', 'genres_raw'
], w=3.3)

p_person = draw_entity(2.5, 16, 'Person', [
    'person_id PK', 'imdb_person_id', 'name', 'birth_year',
    'death_year', 'primary_profession'
], w=3.0)

p_roletype = draw_entity(2.5, 13, 'RoleType', [
    'role_type_id PK', 'role_name'
], w=2.8, color='#8b949e')

p_credit = draw_entity(5.3, 14.2, 'MovieCredit', [
    'credit_id PK', 'movie_id FK', 'person_id FK',
    'role_type_id FK', 'character_name', 'billing_order'
], w=3.0, color=BRIDGE_COLOR)

p_genre = draw_entity(13, 16.5, 'Genre', [
    'genre_id PK', 'genre_name (UNIQUE)'
], w=2.8, color='#8b949e')

p_mg = draw_entity(11, 15, 'MovieGenre', [
    'movie_id FK', 'genre_id FK'
], w=2.5, color=BRIDGE_COLOR)

p_dist = draw_entity(14, 13.5, 'Distributor', [
    'distributor_id PK', 'name', 'address', 'country'
], w=2.8)

p_md = draw_entity(11.5, 12.5, 'MovieDistributor', [
    'movie_id FK', 'distributor_id FK', 'region'
], w=2.8, color=BRIDGE_COLOR)

# === USER LAYER (middle-left) ===

p_user = draw_entity(2.5, 9.5, 'UserProfile', [
    'user_id PK', 'username (UNIQUE)', 'email',
    'age_group', 'preferred_language'
], w=3.0)

p_rating = draw_entity(5.5, 10.5, 'UserRating', [
    'user_id FK PK', 'movie_id FK PK',
    'rating CHECK(0-10)', 'rating_date'
], w=3.0, color=BRIDGE_COLOR)

p_review = draw_entity(5.5, 8.5, 'Review', [
    'review_id PK', 'user_id FK', 'movie_id FK',
    'review_text', 'sentiment', 'review_date'
], w=3.0)

p_extrating = draw_entity(8.5, 12.5, 'ExternalRating', [
    'movie_id FK PK', 'source_name PK',
    'score', 'max_score', 'vote_count'
], w=3.0, color=BRIDGE_COLOR)

# === RECOMMENDATION LAYER (middle) ===

p_tag = draw_entity(17, 10, 'Tag', [
    'tag_id PK', 'tag_name (UNIQUE)'
], w=2.5, color='#8b949e')

p_mtr = draw_entity(14, 10, 'MovieTagRelevance', [
    'movie_id FK PK', 'tag_id FK PK',
    'relevance_score CHECK(0-1)'
], w=3.2, color=BRIDGE_COLOR)

p_upt = draw_entity(17, 7.5, 'UserPreferenceTag', [
    'user_id FK PK', 'tag_id FK PK',
    'preference_weight'
], w=3.0, color=BRIDGE_COLOR)

p_reclog = draw_entity(14, 7.5, 'RecommendationLog', [
    'recommendation_id PK', 'user_id FK',
    'movie_id FK', 'score', 'explanation'
], w=3.2)

# === STREAMING LAYER (middle-right) ===

p_platform = draw_entity(22, 16, 'StreamingPlatform', [
    'platform_id PK', 'name', 'country', 'website_url'
], w=3.0)

p_avail = draw_entity(20, 13.5, 'MovieAvailability', [
    'movie_id FK PK', 'platform_id FK PK',
    'region PK', 'access_type CHECK', 'start_date'
], w=3.2, color=BRIDGE_COLOR)

# === AWARDS LAYER (right) ===

p_award = draw_entity(25.5, 13, 'Award', [
    'award_id PK', 'award_name', 'category'
], w=2.8, color='#8b949e')

p_maward = draw_entity(23, 10.5, 'MovieAward', [
    'movie_award_id PK', 'movie_id FK',
    'award_id FK', 'person_id FK', 'award_year', 'result CHECK'
], w=3.0, color=BRIDGE_COLOR)

# === PRODUCTION LAYER ===

p_prodco = draw_entity(20.5, 10, 'ProductionCompany', [
    'company_id PK', 'name', 'country', 'founded_year'
], w=3.0)

p_mpc = draw_entity(20.5, 7.8, 'MovieProdCompany', [
    'movie_id FK PK', 'company_id FK PK'
], w=3.0, color=BRIDGE_COLOR)

# === WATCHLIST LAYER (bottom-left) ===

p_wl = draw_entity(2.5, 6.5, 'Watchlist', [
    'watchlist_id PK', 'user_id FK', 'name'
], w=2.8)

p_wli = draw_entity(5.5, 5.5, 'WatchlistItem', [
    'watchlist_id FK PK', 'movie_id FK PK',
    'watched_status CHECK'
], w=3.0, color=BRIDGE_COLOR)

# === GROUP WATCH LAYER (bottom) ===

p_wp = draw_entity(9, 5, 'WatchParty', [
    'party_id PK', 'host_user_id FK',
    'party_name', 'planned_date'
], w=3.0)

p_wpm = draw_entity(12.5, 5, 'WatchPartyMember', [
    'party_id FK PK', 'user_id FK PK'
], w=3.0, color=BRIDGE_COLOR)

p_wps = draw_entity(9, 2.5, 'WatchPartySuggestion', [
    'party_id FK PK', 'movie_id FK PK',
    'group_score', 'suggested_by FK'
], w=3.2, color=BRIDGE_COLOR)

# === DRAW RELATIONSHIPS ===

# Movie <-> MovieCredit <-> Person
draw_relation_line(p_movie, p_credit, card1='1', card2='M')
draw_relation_line(p_person, p_credit, card1='1', card2='M')
draw_relation_line(p_roletype, p_credit, card1='1', card2='M')

# Movie <-> MovieGenre <-> Genre
draw_relation_line(p_movie, p_mg, card1='1', card2='M')
draw_relation_line(p_genre, p_mg, card1='1', card2='M')

# Movie <-> MovieDistributor <-> Distributor
draw_relation_line(p_movie, p_md, card1='1', card2='M')
draw_relation_line(p_dist, p_md, card1='1', card2='M')

# Movie <-> UserRating <-> User
draw_relation_line(p_movie, p_rating, card1='1', card2='M')
draw_relation_line(p_user, p_rating, card1='1', card2='M')

# Movie <-> Review <-> User
draw_relation_line(p_movie, p_review, card1='1', card2='M')
draw_relation_line(p_user, p_review, card1='1', card2='M')

# Movie <-> ExternalRating
draw_relation_line(p_movie, p_extrating, card1='1', card2='M')

# Movie <-> MovieTagRelevance <-> Tag
draw_relation_line(p_movie, p_mtr, card1='1', card2='M')
draw_relation_line(p_tag, p_mtr, card1='1', card2='M')

# User <-> UserPreferenceTag <-> Tag
draw_relation_line(p_user, p_upt, card1='1', card2='M')
draw_relation_line(p_tag, p_upt, card1='1', card2='M')

# Movie <-> RecommendationLog <-> User
draw_relation_line(p_movie, p_reclog, card1='1', card2='M')
draw_relation_line(p_user, p_reclog, card1='1', card2='M')

# Movie <-> MovieAvailability <-> Platform
draw_relation_line(p_movie, p_avail, card1='1', card2='M')
draw_relation_line(p_platform, p_avail, card1='1', card2='M')

# Movie <-> MovieAward <-> Award
draw_relation_line(p_movie, p_maward, card1='1', card2='M')
draw_relation_line(p_award, p_maward, card1='1', card2='M')

# Movie <-> MovieProdCompany <-> ProductionCompany
draw_relation_line(p_movie, p_mpc, card1='1', card2='M')
draw_relation_line(p_prodco, p_mpc, card1='1', card2='M')

# User <-> Watchlist -> WatchlistItem -> Movie
draw_relation_line(p_user, p_wl, card1='1', card2='M')
draw_relation_line(p_wl, p_wli, card1='1', card2='M')
draw_relation_line((8, 14.5), p_wli, card1='1', card2='M')  # Movie to WatchlistItem

# User <-> WatchParty
draw_relation_line(p_user, p_wp, card1='1', card2='M')
draw_relation_line(p_wp, p_wpm, card1='1', card2='M')
draw_relation_line(p_user, p_wpm, card1='1', card2='M')
draw_relation_line(p_wp, p_wps, card1='1', card2='M')

# Legend
legend_y = 1.5
ax.text(22, legend_y + 1.2, 'Legend', fontsize=10, fontweight='bold', color=TEXT_COLOR, fontfamily='sans-serif')

legend_items = [
    (ENTITY_COLOR, 'Entity Table'),
    (BRIDGE_COLOR, 'Bridge / Junction Table'),
    (WEAK_COLOR, 'Lookup Table'),
    (PK_COLOR, 'PK  Primary Key'),
    ('#a371f7', 'FK  Foreign Key'),
    ('#f85149', '1 / M  Cardinality'),
]
for i, (c, label) in enumerate(legend_items):
    ly = legend_y + 0.8 - i * 0.35
    ax.add_patch(plt.Rectangle((22, ly - 0.1), 0.3, 0.2, facecolor=c, edgecolor='none'))
    ax.text(22.5, ly, label, va='center', fontsize=7, color=ATTR_COLOR, fontfamily='monospace')

plt.tight_layout()
out = 'docs/database_design/er_diagram.png'
plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='#0d1117', edgecolor='none')
print(f"Saved {out}")
plt.close()
