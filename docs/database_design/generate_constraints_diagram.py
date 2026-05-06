import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(24, 14))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')
ax.set_xlim(0, 24)
ax.set_ylim(0, 14)
ax.axis('off')

TEXT = '#e6edf3'
DIMMED = '#8b949e'
ACCENT = '#58a6ff'

ax.text(12, 13.5, 'CineVerse — Constraints & Data Integrity Summary', ha='center',
        fontsize=16, fontweight='bold', color=ACCENT, fontfamily='sans-serif')

def draw_section(x, y, title, rows, w=7, color='#1f6feb'):
    h = 0.6 + len(rows) * 0.42
    rect = FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.12",
                           facecolor='#161b22', edgecolor=color, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y - 0.25, title, ha='center', va='center',
            fontsize=10, fontweight='bold', color=color, fontfamily='sans-serif')
    for i, (left, right) in enumerate(rows):
        ry = y - 0.65 - i * 0.42
        ax.text(x + 0.2, ry, left, va='center', fontsize=7, color='#f0883e',
                fontfamily='monospace', fontweight='bold')
        ax.text(x + 2.8, ry, right, va='center', fontsize=7, color=TEXT,
                fontfamily='monospace')

# Primary Keys
draw_section(0.5, 12.5, 'PRIMARY KEYS (Surrogate)', [
    ('Movie',           'movie_id SERIAL'),
    ('Person',          'person_id SERIAL'),
    ('Genre',           'genre_id SERIAL'),
    ('UserProfile',     'user_id SERIAL'),
    ('Tag',             'tag_id SERIAL'),
    ('Distributor',     'distributor_id SERIAL'),
    ('StreamingPlatform','platform_id SERIAL'),
    ('Award',           'award_id SERIAL'),
    ('ProductionCompany','company_id SERIAL'),
    ('Watchlist',       'watchlist_id SERIAL'),
    ('WatchParty',      'party_id SERIAL'),
    ('RecommendationLog','recommendation_id SERIAL'),
    ('MovieCredit',     'credit_id SERIAL'),
    ('Review',          'review_id SERIAL'),
    ('MovieAward',      'movie_award_id SERIAL'),
], w=7.2)

# Composite Keys
draw_section(8.2, 12.5, 'COMPOSITE PRIMARY KEYS', [
    ('MovieGenre',        '(movie_id, genre_id)'),
    ('MovieDistributor',  '(movie_id, distributor_id, region)'),
    ('UserRating',        '(user_id, movie_id)'),
    ('ExternalRating',    '(movie_id, source_name)'),
    ('MovieTagRelevance', '(movie_id, tag_id)'),
    ('UserPreferenceTag', '(user_id, tag_id)'),
    ('MovieAvailability', '(movie_id, platform_id, region, access_type)'),
    ('MovieProdCompany',  '(movie_id, company_id)'),
    ('WatchlistItem',     '(watchlist_id, movie_id)'),
    ('WatchPartyMember',  '(party_id, user_id)'),
    ('WatchPartySuggestion','(party_id, movie_id)'),
], w=7.2, color='#238636')

# CHECK constraints
draw_section(16, 12.5, 'CHECK CONSTRAINTS', [
    ('Movie',           'runtime_minutes > 0'),
    ('Movie',           'budget >= 0'),
    ('Movie',           'revenue >= 0'),
    ('Movie',           'imdb_rating BETWEEN 0 AND 10'),
    ('Movie',           'release_year >= 1888'),
    ('UserRating',      'rating BETWEEN 0.0 AND 10.0'),
    ('MovieTagRelevance','relevance_score BETWEEN 0 AND 1'),
    ('UserPreferenceTag','preference_weight BETWEEN 0 AND 1'),
    ('MovieAvailability','access_type IN (subscription,'),
    ('',                 '  rent, buy, free, theater)'),
    ('MovieAward',      'result IN (won, nominated)'),
    ('MovieAward',      'award_year >= 1900'),
    ('WatchlistItem',   'watched_status IN (unwatched,'),
    ('',                 '  watching, watched)'),
    ('UserProfile',     'age_group IN (under_18, 18-24,'),
    ('',                 '  25-34, 35-44, 45-54, 55+)'),
    ('Person',          'death_year >= birth_year'),
    ('MovieCredit',     'billing_order > 0'),
], w=7.5, color='#f85149')

# UNIQUE constraints
draw_section(0.5, 5.2, 'UNIQUE CONSTRAINTS', [
    ('Movie',           'imdb_id UNIQUE NOT NULL'),
    ('Genre',           'genre_name UNIQUE NOT NULL'),
    ('Tag',             'tag_name UNIQUE NOT NULL'),
    ('UserProfile',     'username UNIQUE NOT NULL'),
    ('UserProfile',     'email UNIQUE'),
    ('RoleType',        'role_name UNIQUE NOT NULL'),
    ('StreamingPlatform','(name, country) UNIQUE'),
    ('Award',           '(award_name, category) UNIQUE'),
    ('Review',          '(user_id, movie_id) UNIQUE'),
    ('Watchlist',       '(user_id, name) UNIQUE'),
    ('MovieAward',      '(movie_id, award_id, year) UNIQUE'),
], w=7.2, color='#a371f7')

# Foreign Key Actions
draw_section(8.2, 5.2, 'FOREIGN KEY ACTIONS', [
    ('MovieCredit',     'ON DELETE CASCADE (Movie, Person)'),
    ('MovieGenre',      'ON DELETE CASCADE (Movie, Genre)'),
    ('UserRating',      'ON DELETE CASCADE (User, Movie)'),
    ('WatchlistItem',   'ON DELETE CASCADE (Watchlist)'),
    ('WatchPartyMember','ON DELETE CASCADE (WatchParty)'),
    ('MovieAvailability','ON DELETE CASCADE (Movie, Platform)'),
    ('MovieAward',      'person_id ON DELETE SET NULL'),
    ('WatchPartySugg',  'suggested_by ON DELETE SET NULL'),
], w=7.2, color='#d29922')

# NOT NULL
draw_section(16, 5.2, 'NOT NULL CONSTRAINTS', [
    ('Movie',           'imdb_id, title'),
    ('Person',          'name'),
    ('Genre',           'genre_name'),
    ('RoleType',        'role_name'),
    ('UserProfile',     'username'),
    ('UserRating',      'rating'),
    ('Review',          'review_text'),
    ('Tag',             'tag_name'),
    ('MovieTagRelevance','relevance_score'),
    ('RecommendationLog','score, explanation'),
    ('MovieAvailability','region, access_type'),
    ('MovieAward',      'award_year, result'),
    ('WatchParty',      'party_name'),
], w=7.5, color='#79c0ff')

plt.tight_layout()
out = 'docs/database_design/constraints_summary.png'
plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='#0d1117', edgecolor='none')
print(f"Saved {out}")
plt.close()
