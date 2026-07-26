import { useEffect, useState } from 'react';
import { useLanguage } from '../localization.jsx';
import FilterBar from '../components/FilterBar';

function AllergensPage() {
  const { language, t } = useLanguage();
  const [allergens, setAllergens] = useState([]);
  const [meatTypes, setMeatTypes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);
  const [meatTrackingEnabled, setMeatTrackingEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const [search, setSearch] = useState('');
  const [excludedAllergens, setExcludedAllergens] = useState([]);
  const [selectedMeatTypes, setSelectedMeatTypes] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);

  // Load reference data (allergens, meat types, categories, config) once
  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/allergens').then(res => res.json()),
      fetch('http://localhost:8000/config').then(res => res.json()),
      fetch('http://localhost:8000/meat-types').then(res => res.json()),
      fetch('http://localhost:8000/categories').then(res => res.json()),
    ]).then(([allergensData, configData, meatTypesData, categoriesData]) => {
      setAllergens(allergensData);
      setMeatTrackingEnabled(configData.meat_tracking_enabled);
      setMeatTypes(configData.meat_tracking_enabled ? meatTypesData : []);
      setCategories(categoriesData);
    });
  }, [language]);

  // Refetch items whenever a filter changes
  useEffect(() => {
    setIsLoading(true);

    const params = new URLSearchParams();
    if (search) params.set('search', search);
    excludedAllergens.forEach((code) => params.append('exclude_allergens', code));
    selectedMeatTypes.forEach((code) => params.append('meat_types', code));
    selectedCategories.forEach((code) => params.append('categories', code));

    fetch(`http://localhost:8000/items?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setItems(data);
        setIsLoading(false);
      });
  }, [search, excludedAllergens, selectedMeatTypes, selectedCategories]);

  const toggleAllergen = (code) => {
    setExcludedAllergens((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const toggleMeatType = (code) => {
    setSelectedMeatTypes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const toggleCategory = (code) => {
    setSelectedCategories((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const uncategorizedLabel = language === 'nl' ? 'Overig' : 'Uncategorized';

  const getCategoryLabel = (key) => {
    if (!key) return uncategorizedLabel;
    const category = categories.find((c) => c.code === key);
    if (!category) return key;
    return language === 'nl' ? category.description_nl : category.description_en;
  };

  let lastCategory = null;

  return (
    <div className="app">
      <FilterBar
        search={search}
        onSearchChange={setSearch}
        allergens={allergens}
        excludedAllergens={excludedAllergens}
        onToggleAllergen={toggleAllergen}
        meatTypes={meatTypes}
        meatTrackingEnabled={meatTrackingEnabled}
        selectedMeatTypes={selectedMeatTypes}
        onToggleMeatType={toggleMeatType}
        categories={categories}
        selectedCategories={selectedCategories}
        onToggleCategory={toggleCategory}
        language={language}
        t={t}
      />

      {isLoading ? (
        <p className="loading-message">{t.loading}</p>
      ) : (
        <>
          {/* Desktop: table view */}
          <div className="matrix-wrapper matrix-desktop-view">
            <table className="allergen-matrix">
              <thead>
                <tr>
                  <th className="matrix-corner"></th>
                  {allergens.map((allergen) => (
                    <th key={allergen.id} className="matrix-allergen-header">
                      <img
                        src={`http://localhost:8000/static/icons/${allergen.code}.png`}
                        alt={language === 'nl' ? allergen.description_nl : allergen.description_en}
                        title={language === 'nl' ? allergen.description_nl : allergen.description_en}
                        className="matrix-icon"
                      />
                    </th>
                  ))}
                  {meatTrackingEnabled && meatTypes.map((meatType) => (
                    <th key={`meat-${meatType.id}`} className="matrix-meat-header">
                      <img
                        src={`http://localhost:8000/static/icons/meat/${meatType.code}.png`}
                        alt={language === 'nl' ? meatType.description_nl : meatType.description_en}
                        title={language === 'nl' ? meatType.description_nl : meatType.description_en}
                        className="matrix-icon"
                      />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {items.map((item) => {
                  const itemAllergenIds = item.allergens.map((a) => a.id);
                  const itemMeatTypeIds = item.meat_types.map((m) => m.id);
                  const categoryLabel = getCategoryLabel(item.category_key);
                  const showCategoryHeader = categoryLabel !== lastCategory;
                  lastCategory = categoryLabel;

                  const columnCount = 1 + allergens.length + (meatTrackingEnabled ? meatTypes.length : 0);

                  return (
                    <>
                      {showCategoryHeader && (
                        <tr key={`category-${categoryLabel}`} className="matrix-category-row">
                          <td colSpan={columnCount} className="matrix-category-label">
                            {categoryLabel}
                          </td>
                        </tr>
                      )}
                      <tr key={item.id}>
                        <td className="matrix-item-name">{item.name}</td>
                        {allergens.map((allergen) => (
                          <td key={allergen.id} className="matrix-cell">
                            {itemAllergenIds.includes(allergen.id) ? '●' : ''}
                          </td>
                        ))}
                        {meatTrackingEnabled && meatTypes.map((meatType) => (
                          <td key={`meat-${meatType.id}`} className="matrix-cell">
                            {itemMeatTypeIds.includes(meatType.id) ? '●' : ''}
                          </td>
                        ))}
                      </tr>
                    </>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Mobile: card view */}
          <div className="matrix-mobile-view">
            {items.map((item) => {
              const categoryLabel = getCategoryLabel(item.category_key);
              const showCategoryHeader = categoryLabel !== lastCategory;
              lastCategory = categoryLabel;

              return (
                <>
                  {showCategoryHeader && (
                    <h2 key={`mobile-category-${categoryLabel}`} className="mobile-category-label">
                      {categoryLabel}
                    </h2>
                  )}
                  <div key={item.id} className="item-card">
                    <span className="item-card-name">{item.name}</span>

                    {item.allergens.length > 0 ? (
                      <div className="item-card-tags">
                        {item.allergens.map((allergen) => (
                          <span key={allergen.id} className="item-card-tag">
                            <img
                              src={`http://localhost:8000/static/icons/${allergen.code}.png`}
                              alt={language === 'nl' ? allergen.description_nl : allergen.description_en}
                              className="item-card-tag-icon"
                            />
                            {language === 'nl' ? allergen.description_nl : allergen.description_en}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="no-allergens">{t.noAllergens}</p>
                    )}

                    {meatTrackingEnabled && item.meat_types.length > 0 && (
                      <div className="item-card-tags item-card-meat-tags">
                        {item.meat_types.map((meatType) => (
                          <span key={meatType.id} className="item-card-tag item-card-meat-tag">
                            <img
                              src={`http://localhost:8000/static/icons/meat/${meatType.code}.png`}
                              alt={language === 'nl' ? meatType.description_nl : meatType.description_en}
                              className="item-card-tag-icon"
                            />
                            {language === 'nl' ? meatType.description_nl : meatType.description_en}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              );
            })}
          </div>
        </>
      )}

      <div className="legend-section">
        <div className="legend">
          <span className="legend-item">
            <span className="legend-dot">●</span>
            {language === 'nl' ? ' Bevat dit allergeen' : ' Contains this allergen'}
          </span>
        </div>

        <h2 className="allergen-key-title">
          {language === 'nl' ? 'Allergenen' : 'Allergens'}
        </h2>
        <div className="allergen-key">
          {allergens.map((allergen) => (
            <span key={allergen.id} className="allergen-key-item">
              <img
                src={`http://localhost:8000/static/icons/${allergen.code}.png`}
                alt={language === 'nl' ? allergen.description_nl : allergen.description_en}
                className="allergen-key-icon"
              />
              {language === 'nl' ? allergen.description_nl : allergen.description_en}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AllergensPage;