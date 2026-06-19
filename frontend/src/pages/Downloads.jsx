import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import DownloadCard from '../components/common/DownloadCard.jsx';
import useDownloads from '../hooks/useDownloads.js';

// Map dataset filenames to human-readable categories and descriptions
function categorize(dataset) {
  const name = (dataset || '').toLowerCase();
  if (name.includes('forecast') || name.includes('prediction')) {
    return { category: 'Forecast', description: 'LightGBM forecast outputs and predicted violation counts.' };
  }
  if (name.includes('patrol')) {
    return { category: 'Patrol', description: 'AI-ranked patrol deployment recommendations.' };
  }
  if (name.includes('risk') || name.includes('congestion')) {
    return { category: 'Risk Zones', description: 'Congestion risk scores and category classifications.' };
  }
  if (name.includes('station')) {
    return { category: 'Stations', description: 'Police station analytics and operational metrics.' };
  }
  if (name.includes('junction')) {
    return { category: 'Junctions', description: 'Junction-level case volume and approval statistics.' };
  }
  if (name.includes('stability')) {
    return { category: 'Stability', description: 'Hotspot stability classifications from 6-month history.' };
  }
  if (name.includes('feature') || name.includes('importance')) {
    return { category: 'Explainability', description: 'LightGBM feature importance and model insights.' };
  }
  if (name.includes('hotspot')) {
    return { category: 'Hotspots', description: 'Spatial hotspot intelligence and map data.' };
  }
  return { category: 'Dataset', description: 'Precomputed analytics dataset.' };
}

// Group datasets by category
function groupDatasets(datasets) {
  const groups = {};
  datasets.forEach((dataset) => {
    const { category, description } = categorize(dataset);
    if (!groups[category]) groups[category] = [];
    groups[category].push({ dataset, description });
  });
  return groups;
}

export default function Downloads() {
  const { datasets, loading, error } = useDownloads();

  if (loading) return <LoadingSkeleton height="h-[400px]" />;
  if (error) return <ErrorState message={error} />;

  const grouped = groupDatasets(datasets);

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Data Export"
        title="Dataset Downloads"
        subtitle="Download precomputed analytics datasets as CSV files for offline analysis."
      />

      {/* Ungrouped fallback if all in one category */}
      {Object.keys(grouped).length <= 1 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {datasets.map((dataset, index) => {
            const { description } = categorize(dataset);
            return (
              <DownloadCard key={index} dataset={dataset} description={description} />
            );
          })}
        </div>
      ) : (
        Object.entries(grouped).map(([category, items]) => (
          <div key={category} className="space-y-3">
            <p
              className="font-mono text-[12px] font-semibold uppercase"
              style={{ color: '#00d992', letterSpacing: '2px' }}
            >
              {category}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {items.map(({ dataset, description }, index) => (
                <DownloadCard
                  key={index}
                  dataset={dataset}
                  description={description}
                  category={category}
                />
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
