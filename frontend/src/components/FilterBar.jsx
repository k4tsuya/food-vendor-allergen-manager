function FilterBar({
  search,
  onSearchChange,
  allergens,
  excludedAllergens,
  onToggleAllergen,
  meatTypes,
  meatTrackingEnabled,
  selectedMeatTypes,
  onToggleMeatType,
  categories,
  categoryLabels,
  selectedCategories,
  onToggleCategory,
  language,
  t,
}) {
  return (
    <div className="filter-bar">
      <input
        type="text"
        className="filter-search"
        placeholder={language === 'nl' ? 'Zoek op naam...' : 'Search by name...'}
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
      />

      {categories.length > 0 && (
        <div className="filter-group">
          <span className="filter-group-label">
            {language === 'nl' ? 'Categorie' : 'Category'}
          </span>
          <div className="filter-chips">
          {categories.map((category) => (
            <label key={category.code} className="filter-chip">
              <input
                type="checkbox"
                checked={selectedCategories.includes(category.code)}
                onChange={() => onToggleCategory(category.code)}
              />
              {language === 'nl' ? category.description_nl : category.description_en}
            </label>
          ))}
          </div>
        </div>
      )}

      <div className="filter-group">
        <span className="filter-group-label">
          {language === 'nl' ? 'Allergenen uitsluiten' : 'Exclude allergens'}
        </span>
        <div className="filter-chips">
          {allergens.map((allergen) => (
            <label key={allergen.id} className="filter-chip">
              <input
                type="checkbox"
                checked={excludedAllergens.includes(allergen.code)}
                onChange={() => onToggleAllergen(allergen.code)}
              />
              {language === 'nl' ? allergen.description_nl : allergen.description_en}
            </label>
          ))}
        </div>
      </div>

      {meatTrackingEnabled && meatTypes.length > 0 && (
        <div className="filter-group">
          <span className="filter-group-label">
            {language === 'nl' ? 'Vleessoort' : 'Meat type'}
          </span>
          <div className="filter-chips">
            {meatTypes.map((meatType) => (
              <label key={meatType.id} className="filter-chip">
                <input
                  type="checkbox"
                  checked={selectedMeatTypes.includes(meatType.code)}
                  onChange={() => onToggleMeatType(meatType.code)}
                />
                {language === 'nl' ? meatType.description_nl : meatType.description_en}
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FilterBar;