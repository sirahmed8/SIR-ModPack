import { MetadataRoute } from 'next';

export const dynamic = 'force-static';

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://sir-modpack.web.app';
  const currentDate = new Date().toISOString();

  const routes = [
    '',
    '/profiles',
    '/shaders',
    '/mods',
    '/servers',
    '/benchmarks',
    '/compatibility',
    '/capes',
    '/skins',
    '/seeds',
    '/leaderboards',
    '/trainer',
    '/builder',
    '/server-guide',
    '/faq',
    '/news',
    '/changelog',
    '/terms',
    '/privacy',
    '/cookies'
  ];

  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: currentDate,
    changeFrequency: route === '' || route === '/news' || route === '/leaderboards' ? 'daily' : 'weekly',
    priority: route === '' ? 1.0 : (route === '/profiles' || route === '/shaders' || route === '/mods' ? 0.9 : 0.8),
  }));
}
