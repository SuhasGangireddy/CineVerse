import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(26, 16))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')
ax.set_xlim(0, 26)
ax.set_ylim(0, 16)
ax.axis('off')

TEXT = '#e6edf3'
ACCENT = '#58a6ff'

ax.text(13, 15.5, 'CineVerse — Relational Schema Mapping', ha='center',
        fontsize=16, fontweight='bold', color=ACCENT, fontfamily='sans-serif')
ax.text(13, 15.1, 'Conceptual Entity → Relational Table  |  27 Tables', ha='center',
        fontsize=9, color='#8b949e', fontfamily='sans-serif')

def draw_mapping_group(x, y, group_title, mappings, w=12, color='#1f6feb'):
    row_h = 0.38
    h = 0.5 + len(mappings) * row_h
    rect = FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.1",
                           facecolor='#161b22', edgecolor=color, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y - 0.22, group_title, ha='center', va='center',
            fontsize=10, fontweight='bold', color=color, fontfamily='sans-serif')

    # column headers
    hy = y - 0.55
    ax.text(x + 0.2, hy, 'Concept', va='center', fontsize=6.5, color='#484f58',
            fontfamily='monospace', fontweight='bold')
    ax.text(x + 2.8, hy, 'Table', va='center', fontsize=6.5, color='#484f58',
            fontfamily='monospace', fontweight='bold')
    ax.text(x + 5.5, hy, 'Type', va='center', fontsize=6.5, color='#484f58',
            fontfamily='monospace', fontweight='bold')
    ax.text(x + 7, hy, 'Key Columns', va='center', fontsize=6.5, color='#484f58',
            fontfamily='monospace', fontweight='bold')

    for i, (concept, table, ttype, keys) in enumerate(mappings):
        ry = y - 0.85 - i * row_h
        bg_alpha = 0.03 if i % 2 == 0 else 0
        if bg_alpha:
            ax.add_patch(plt.Rectangle((x + 0.05, ry - 0.15), w - 0.1, row_h,
                                        facecolor='white', alpha=bg_alpha, edgecolor='none'))

        ax.text(x + 0.2, ry, concept, va='center', fontsize=7, color=TEXT,
                fontfamily='monospace')

        type_colors = {'Entity': '#1f6feb', 'Bridge': '#238636', 'Lookup': '#8b949e'}
        tc = type_colors.get(ttype, '#8b949e')

        ax.text(x + 2.8, ry, table, va='center', fontsize=7, color='#f0883e',
                fontfamily='monospace', fontweight='bold')
        ax.text(x + 5.5, ry, ttype, va='center', fontsize=6.5, color=tc,
                fontfamily='monospace')
        ax.text(x + 7, ry, keys, va='center', fontsize=6.5, color='#8b949e',
                fontfamily='monospace')

# Core layer
draw_mapping_group(0.5, 14.5, 'Core: Movie Catalog & Credits', [
    ('Movie',            'Movie',            'Entity', 'movie_id PK, imdb_id UK, title, year, runtime'),
    ('Person',           'Person',           'Entity', 'person_id PK, name, birth_year, profession'),
    ('Role',             'RoleType',         'Lookup', 'role_type_id PK, role_name (Actor/Dir/Prod/Writer)'),
    ('Movie-Person M:N', 'MovieCredit',     'Bridge', 'credit_id PK → movie_id FK, person_id FK, role FK'),
    ('Genre',            'Genre',            'Lookup', 'genre_id PK, genre_name UK'),
    ('Movie-Genre M:N',  'MovieGenre',      'Bridge', '(movie_id, genre_id) composite PK'),
    ('Distributor',      'Distributor',      'Entity', 'distributor_id PK, name, address, country'),
    ('Movie-Dist M:N',   'MovieDistributor','Bridge', '(movie_id, distributor_id, region) composite PK'),
], w=12.3)

# User layer
draw_mapping_group(13.2, 14.5, 'Users: Ratings, Reviews, Preferences', [
    ('User Account',     'UserProfile',     'Entity', 'user_id PK, username UK, email UK, age_group'),
    ('User Rating',      'UserRating',      'Bridge', '(user_id, movie_id) PK, rating CHECK 0-10'),
    ('Written Review',   'Review',          'Entity', 'review_id PK, user→movie FK, text, sentiment'),
    ('External Score',   'ExternalRating',  'Bridge', '(movie_id, source_name) PK, score, vote_count'),
    ('Mood/Theme Tag',   'Tag',             'Lookup', 'tag_id PK, tag_name UK'),
    ('Movie-Tag score',  'MovieTagRelevance','Bridge','(movie_id, tag_id) PK, relevance_score 0-1'),
    ('User Preference',  'UserPreferenceTag','Bridge','(user_id, tag_id) PK, preference_weight'),
    ('Recommendation',   'RecommendationLog','Entity','rec_id PK, user FK, movie FK, score, explanation'),
], w=12.3)

# Availability & Awards
draw_mapping_group(0.5, 10, 'Streaming, Awards & Production', [
    ('Platform',          'StreamingPlatform', 'Entity', 'platform_id PK, name, country, url'),
    ('Movie-Platform M:N','MovieAvailability', 'Bridge', '(movie_id, platform_id, region, access) PK'),
    ('Award Ceremony',    'Award',             'Lookup', 'award_id PK, (award_name, category) UK'),
    ('Movie Award',       'MovieAward',        'Bridge', 'movie_award_id PK, movie→award FK, year, result'),
    ('Studio',            'ProductionCompany', 'Entity', 'company_id PK, name, country, founded_year'),
    ('Movie-Studio M:N',  'MovieProductionCo','Bridge', '(movie_id, company_id) composite PK'),
], w=12.3)

# Watchlist & Group
draw_mapping_group(13.2, 10, 'Watchlist & Group Watch', [
    ('Watchlist',         'Watchlist',         'Entity', 'watchlist_id PK, user_id FK, name'),
    ('Saved Movie',       'WatchlistItem',     'Bridge', '(watchlist_id, movie_id) PK, watched_status'),
    ('Watch Party',       'WatchParty',        'Entity', 'party_id PK, host_user FK, name, date'),
    ('Party Member',      'WatchPartyMember',  'Bridge', '(party_id, user_id) composite PK'),
    ('Group Suggestion',  'WatchPartySuggestion','Bridge','(party_id, movie_id) PK, group_score'),
], w=12.3)

# Cardinality summary
cy = 5.8
ax.text(13, cy + 0.3, 'Key Relationships & Cardinalities', ha='center',
        fontsize=12, fontweight='bold', color=ACCENT, fontfamily='sans-serif')

rels = [
    ('Movie', '1', 'M', 'MovieCredit', 'M', '1', 'Person',    'A movie has many credits; a person has many credits'),
    ('Movie', '1', 'M', 'MovieGenre',  'M', '1', 'Genre',     'Many-to-many: a movie can have multiple genres'),
    ('Movie', '1', 'M', 'UserRating',  'M', '1', 'UserProfile','Each user rates each movie at most once (composite PK)'),
    ('Movie', '1', 'M', 'MovieAvailability','M','1','StreamingPlatform', 'Available on multiple platforms per region'),
    ('Movie', '1', 'M', 'MovieAward',  'M', '1', 'Award',     'A movie can win/be nominated for many awards'),
    ('UserProfile','1','M','Watchlist', '1', 'M', 'WatchlistItem', 'User owns watchlists containing many movies'),
    ('WatchParty','1','M','WatchPartyMember','M','1','UserProfile', 'A party has many members; user joins many parties'),
    ('Movie', '1', 'M', 'MovieTagRelevance','M','1','Tag',     'Mood tags scored per movie for recommendations'),
]

for i, (e1, c1, c2, bridge, c3, c4, e2, desc) in enumerate(rels):
    ry = cy - 0.4 - i * 0.4
    ax.text(1, ry, e1, va='center', fontsize=7.5, color='#f0883e', fontfamily='monospace', fontweight='bold')
    ax.text(3.5, ry, f'({c1})', va='center', fontsize=7, color='#f85149', fontfamily='monospace')
    ax.text(4.1, ry, '——', va='center', fontsize=7, color='#484f58', fontfamily='monospace')
    ax.text(4.7, ry, f'({c2})', va='center', fontsize=7, color='#f85149', fontfamily='monospace')
    ax.text(5.3, ry, bridge, va='center', fontsize=7, color='#238636', fontfamily='monospace')
    ax.text(8.5, ry, f'({c3})', va='center', fontsize=7, color='#f85149', fontfamily='monospace')
    ax.text(9.1, ry, '——', va='center', fontsize=7, color='#484f58', fontfamily='monospace')
    ax.text(9.7, ry, f'({c4})', va='center', fontsize=7, color='#f85149', fontfamily='monospace')
    ax.text(10.3, ry, e2, va='center', fontsize=7.5, color='#f0883e', fontfamily='monospace', fontweight='bold')
    ax.text(14, ry, desc, va='center', fontsize=6.5, color=TEXT, fontfamily='monospace')

plt.tight_layout()
out = 'docs/database_design/relational_mapping.png'
plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='#0d1117', edgecolor='none')
print(f"Saved {out}")
plt.close()
