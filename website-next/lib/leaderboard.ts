import { db, rtdb } from "@/lib/firebase";
import { 
  collection, 
  addDoc, 
  getDocs, 
  query, 
  orderBy, 
  limit, 
  serverTimestamp 
} from "firebase/firestore";
import { 
  ref, 
  set, 
  get, 
  serverTimestamp as rtdbServerTimestamp 
} from "firebase/database";

export interface BenchmarkRecord {
  id: string;
  username: string;
  category: "cps" | "aim" | "reaction";
  score: number;
  formattedScore: string;
  accuracy?: number;
  timestamp: number;
  verified: boolean;
  avatarUrl: string;
  rankTitle?: string;
  isUserRun?: boolean;
}

export function getLocalBenchmarkRecords(): BenchmarkRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem("sir_benchmark_records");
    if (!raw) return [];
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export async function recordBenchmarkScore(
  username: string,
  category: "cps" | "aim" | "reaction",
  score: number,
  accuracy: number = 100,
  rankTitle?: string
): Promise<BenchmarkRecord> {
  const cleanUsername = (username || "Player").trim() || "Player";
  let formatted = `${score}`;
  if (category === "cps") formatted = `${score.toFixed(1)} CPS`;
  if (category === "aim") formatted = `${Math.round(score)} ms Reflex`;
  if (category === "reaction") formatted = `${Math.round(score)} ms`;

  const recordId = `rec_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;

  const newRecord: BenchmarkRecord = {
    id: recordId,
    username: cleanUsername,
    category,
    score,
    formattedScore: formatted,
    accuracy,
    timestamp: Date.now(),
    verified: true,
    avatarUrl: `https://mc-heads.net/avatar/${cleanUsername}/64`,
    rankTitle,
    isUserRun: true
  };

  // 1. Save to LocalStorage (Personal Best logic)
  if (typeof window !== "undefined") {
    try {
      const existing = getLocalBenchmarkRecords();
      const userKey = cleanUsername.toLowerCase();
      const existingIdx = existing.findIndex(
        r => (r.username || "").trim().toLowerCase() === userKey && r.category === category
      );

      let updated: BenchmarkRecord[];
      if (existingIdx >= 0) {
        const prev = existing[existingIdx];
        const isBetter = category === "cps" 
          ? score >= prev.score 
          : score <= prev.score;

        if (isBetter) {
          existing[existingIdx] = newRecord;
          updated = [...existing];
        } else {
          updated = existing;
        }
      } else {
        updated = [newRecord, ...existing];
      }

      localStorage.setItem("sir_benchmark_records", JSON.stringify(updated.slice(0, 100)));
      window.dispatchEvent(new CustomEvent("sir_benchmark_saved", { detail: newRecord }));
    } catch (e) {
      console.warn("Could not save to localStorage", e);
    }
  }

  // 2. Push to Firestore
  try {
    if (db) {
      await addDoc(collection(db, "leaderboard_records"), {
        ...newRecord,
        createdAt: serverTimestamp()
      });
    }
  } catch (err) {
    console.warn("Firestore save warning:", err);
  }

  // 3. Push to Realtime Database for instant global syncing
  try {
    if (rtdb) {
      const rtdbPath = ref(rtdb, `leaderboards/${category}/${recordId}`);
      await set(rtdbPath, {
        ...newRecord,
        createdAt: rtdbServerTimestamp()
      });
    }
  } catch (err) {
    console.warn("RTDB leaderboard save warning:", err);
  }

  return newRecord;
}

export async function fetchAllLeaderboardRecords(): Promise<BenchmarkRecord[]> {
  const localItems = getLocalBenchmarkRecords();
  const recordsMap: { [key: string]: BenchmarkRecord } = {};

  // Add local items
  localItems.forEach(item => {
    recordsMap[item.id] = item;
  });

  // Fetch from Realtime Database first
  try {
    if (rtdb) {
      const snap = await get(ref(rtdb, "leaderboards"));
      if (snap.exists()) {
        const data = snap.val();
        for (const cat in data) {
          for (const recId in data[cat]) {
            const r = data[cat][recId];
            if (r?.username && r?.score !== undefined) {
              recordsMap[recId] = {
                id: recId,
                username: r.username,
                category: r.category || cat,
                score: r.score,
                formattedScore: r.formattedScore || `${r.score}`,
                accuracy: r.accuracy || 100,
                timestamp: r.timestamp || Date.now(),
                verified: r.verified !== false,
                avatarUrl: r.avatarUrl || `https://mc-heads.net/avatar/${r.username}/64`,
                rankTitle: r.rankTitle
              };
            }
          }
        }
      }
    }
  } catch (e) {
    console.warn("RTDB leaderboard fetch notice:", e);
  }

  // Also query Firestore for any additional records
  try {
    if (db) {
      const q = query(collection(db, "leaderboard_records"), orderBy("timestamp", "desc"), limit(80));
      const snap = await getDocs(q);
      snap.forEach(doc => {
        const d = doc.data();
        recordsMap[doc.id] = {
          id: doc.id,
          username: d.username || "Player",
          category: d.category || "cps",
          score: d.score || 0,
          formattedScore: d.formattedScore || `${d.score}`,
          accuracy: d.accuracy || 100,
          timestamp: d.timestamp || Date.now(),
          verified: d.verified !== false,
          avatarUrl: d.avatarUrl || `https://mc-heads.net/avatar/${d.username || "Steve"}/64`,
          rankTitle: d.rankTitle
        };
      });
    }
  } catch (err) {
    console.warn("Firestore fetch warning:", err);
  }

  const allRaw = Object.values(recordsMap);

  // 1. Purge fake/test accounts (e.g. SirPlayer with fake warmup times)
  const filteredRaw = allRaw.filter(r => {
    const u = (r.username || "").trim().toLowerCase();
    return u && u !== "sirplayer" && u !== "test" && u !== "fake" && u !== "undefined" && !u.includes("test");
  });

  // 2. Group by user + category so each player has strictly ONE single highest personal best
  const bestMap: { [userCatKey: string]: BenchmarkRecord } = {};

  filteredRaw.forEach(rec => {
    const key = `${rec.username.trim().toLowerCase()}_${rec.category}`;
    const existing = bestMap[key];

    if (!existing) {
      bestMap[key] = rec;
    } else {
      // Comparison: For CPS higher is better; For aim/reaction lower ms is better
      if (rec.category === "cps") {
        if (rec.score > existing.score) {
          bestMap[key] = rec;
        }
      } else {
        if (rec.score < existing.score) {
          bestMap[key] = rec;
        }
      }
    }
  });

  return Object.values(bestMap);
}
