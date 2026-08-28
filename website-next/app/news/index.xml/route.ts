import { GET as getNews } from "../../api/news/route";

export const dynamic = "force-static";

export async function GET(request: Request) {
  return getNews(request);
}
