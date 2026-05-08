import authHeroImage from '../../../assets/images/start.png';

export function AuthIllustration() {
  return (
    <div className="relative hidden min-h-screen overflow-hidden border-l border-slate-800/80 bg-[#06101a] lg:block">
      <img className="h-full min-h-screen w-full object-cover" src={authHeroImage} alt="FactoryGuard smart factory control room" />
      <div className="absolute inset-0 bg-gradient-to-r from-[#06101a]/55 via-[#06101a]/10 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-t from-[#03070b]/70 via-transparent to-[#03070b]/30" />
      <div className="absolute left-10 top-10 rounded-full border border-blue-400/30 bg-blue-500/10 px-5 py-2 text-[13px] font-black tracking-[0.24em] text-blue-300 backdrop-blur-md">
        FACTORYGUARD
      </div>
    </div>
  );
}
