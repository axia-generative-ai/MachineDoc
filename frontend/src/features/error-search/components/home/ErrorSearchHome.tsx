import { RecentSearchPanel } from './RecentSearchPanel';
import { SearchGuideGrid } from './SearchGuideGrid';
import { SearchHero } from './SearchHero';

export function ErrorSearchHome() {
  return (
    <div className="mx-auto max-w-[1320px] ">
      <SearchHero />

      <div className="mt-6 grid gap-5 lg:grid-cols-[420px_1fr]">
        <RecentSearchPanel />
        <SearchGuideGrid />
      </div>
    </div>
  );
}
