import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useTranslation } from 'react-i18next';

ChartJS.register(ArcElement, Tooltip, Legend);

const DonutChart: React.FC = () => {
  const { t } = useTranslation();
  const data = {
    labels: [t('dashboard'), t('myFarms'), t('ownership'), t('marketplace')],
    datasets: [
      {
        data: [30, 20, 25, 25],
        backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
        hoverBackgroundColor: ['#2563EB', '#059669', '#D97706', '#DC2626'],
      },
    ],
  };

  return (
    <div className="max-w-sm mx-auto">
      <Doughnut data={data} />
    </div>
  );
};

export default DonutChart;
