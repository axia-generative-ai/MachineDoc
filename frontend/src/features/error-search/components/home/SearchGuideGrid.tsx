import { searchGuideCards } from '../../model/errorSearchHomeData';
import { Panel } from '../../../../shared/ui/Panel';

export function SearchGuideGrid() {
  return (
    <div className="grid gap-5 md:grid-cols-2">
      {searchGuideCards.map((card) => {
        const Icon = card.icon;

        return (
          <Panel key={card.title} className="p-5">
            <div className="mb-4 grid h-12 w-12 place-items-center rounded-full bg-blue-500/10 text-blue-400">
              <Icon className="h-7 w-7" />
            </div>
            <h3 className="text-[20px] font-black tracking-[-0.05em] text-white">{card.title}</h3>
            <p className="mt-3 text-[15px] font-semibold leading-6 text-slate-400">{card.description}</p>
          </Panel>
        );
      })}
    </div>
  );
}

