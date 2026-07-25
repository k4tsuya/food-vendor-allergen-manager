import { useEffect, useState } from 'react';
import { useLanguage } from '../localization.jsx';

function AllergensPage() {
  const { language, t } = useLanguage();
  const [allergens, setAllergens] = useState([]);
  const [meatTypes, setMeatTypes] = useState([]);
  const [items, setItems] = useState([]);
  const [itemLabel, setItemLabel] = useState('Item');
  const [meatTrackingEnabled, setMeatTrackingEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/allergens').then(res => res.json()),
      fetch('http://localhost:8000/items').then(res => res.json()),
      fetch('http://localhost:8000/config').then(res => res.json()),
      fetch('http://localhost:8000/meat-types').then(res => res.json()),
    ]).then(([allergensData, itemsData, configData, meatTypesData]) => {
      setAllergens(allergensData);
      setItems(itemsData);
      setItemLabel(language === 'nl' ? configData.item_label_nl : configData.item_label_en);
      setMeatTrackingEnabled(configData.meat_tracking_enabled);
      setMeatTypes(configData.meat_tracking_enabled ? meatTypesData : []);
      setIsLoading(false);
    });
  }, [language]);

  if (isLoading) {
    return <p className="loading-message">{t.loading}</p>;
  }

  return (
    <div className="app">
      <div className="matrix-wrapper">
        <table className="allergen-matrix">
          <thead>
            <tr>
              <th className="matrix-corner">{itemLabel}</th>
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

              return (
                <tr key={item.id}>
                  <td className="matrix-item-name">{item.name}</td>
                  {allergens.map((allergen) => (
                    <td key={allergen.id} className="matrix-cell">
                      {itemAllergenIds.includes(allergen.id) ? '●' : ''}
                    </td>
                  ))}
                  {meatTrackingEnabled && meatTypes.map((meatType) => (
                    <td key={`meat-${meatType.id}`} className="matrix-cell matrix-meat-cell">
                      {itemMeatTypeIds.includes(meatType.id) ? '●' : ''}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

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