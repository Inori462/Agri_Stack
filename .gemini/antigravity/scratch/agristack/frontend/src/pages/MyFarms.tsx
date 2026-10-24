import React from 'react';
import { useTranslation } from 'react-i18next';

const MyFarms: React.FC = () => {
  const { t } = useTranslation();
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">{t('myFarms')}</h2>
      <p className="text-gray-700">List of farms will appear here.</p>
    </div>
  );
};

export default MyFarms;
