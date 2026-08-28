import { HeroDownload } from "@/components/HeroDownload";
import { ProfilesMatrix } from "@/components/ProfilesMatrix";
import { AccountLinking } from "@/components/AccountLinking";
import { ServerHostingPortal } from "@/components/ServerHostingPortal";
import { HavocPortal } from "@/components/HavocPortal";
import { ChangelogSection } from "@/components/ChangelogSection";
import { MainPageQuickDock } from "@/components/MainPageQuickDock";

export default function Home() {
  return (
    <div className="space-y-4 relative">
      <MainPageQuickDock />
      <HeroDownload />
      <ProfilesMatrix />
      <AccountLinking />
      <ServerHostingPortal />
      <HavocPortal />
      <ChangelogSection />
    </div>
  );
}
