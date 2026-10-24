import React from 'react';
import { useTranslation } from 'react-i18next';

const Marketplace: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">{t('marketplace')}</h2>
      <p className="text-gray-700">Marketplace listings will be shown here.</p>
    </div>
  );
};

export default Marketplace;
