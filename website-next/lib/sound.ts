// Sound system completely removed as requested
export const soundFx = {
  isEnabled: (): boolean => false,
  setEnabled: (_enabled: boolean): void => {},
  playClick: (): void => {},
  playTab: (): void => {},
  playSuccess: (): void => {},
  playCelebration: (): void => {},
  playWarp: (): void => {},
  playError: (): void => {}
};
