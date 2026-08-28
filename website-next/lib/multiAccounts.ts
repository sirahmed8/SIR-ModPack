import { db, rtdb } from "./firebase";
import { 
  doc, 
  setDoc, 
  getDoc, 
  collection, 
  getDocs, 
  deleteDoc, 
  serverTimestamp 
} from "firebase/firestore";
import { 
  ref, 
  set, 
  get, 
  remove, 
  serverTimestamp as rtdbServerTimestamp 
} from "firebase/database";

export interface ClaimedAccountItem {
  id?: string;
  ign: string;
  skinUrl: string;
  model: "classic" | "slim";
  accountType?: "offline" | "microsoft" | "claimed";
  createdAt?: any;
}

/**
 * Saves or updates a claimed Minecraft username under a user's multi-account cloud profile.
 */
export async function saveClaimedAccountToCloud(
  uid: string,
  userEmail: string | null,
  account: ClaimedAccountItem
): Promise<void> {
  const cleanIgn = account.ign.trim();
  if (!cleanIgn) return;

  const dataToSave = {
    ign: cleanIgn,
    skinUrl: account.skinUrl || `https://mc-heads.net/skin/${encodeURIComponent(cleanIgn)}`,
    model: account.model || "classic",
    accountType: account.accountType || "offline",
    updatedAt: serverTimestamp()
  };

  // 1. Firestore: Save to subcollection users/{uid}/claimedAccounts/{ign}
  try {
    const docRef = doc(db, "users", uid, "claimedAccounts", cleanIgn);
    await setDoc(docRef, dataToSave, { merge: true });
  } catch (e) {
    console.warn("Firestore subcollection save notice:", e);
  }

  // 2. Realtime Database: Save under users/{uid}/claimedAccounts/{ign}
  try {
    const rtdbRef = ref(rtdb, `users/${uid}/claimedAccounts/${cleanIgn}`);
    await set(rtdbRef, {
      ...dataToSave,
      updatedAt: rtdbServerTimestamp()
    });
  } catch (e) {
    console.warn("RTDB user claimedAccounts save notice:", e);
  }

}

/**
 * Retrieves all claimed Minecraft usernames for a user from Firestore & RTDB.
 */
export async function getClaimedAccountsFromCloud(
  uid: string
): Promise<ClaimedAccountItem[]> {
  const accountsMap: { [key: string]: ClaimedAccountItem } = {};

  // Try Realtime Database first for speed
  try {
    const rtdbRef = ref(rtdb, `users/${uid}/claimedAccounts`);
    const snap = await get(rtdbRef);
    if (snap.exists()) {
      const data = snap.val();
      for (const k in data) {
        if (data[k]?.ign) {
          accountsMap[data[k].ign.toLowerCase()] = {
            ign: data[k].ign,
            skinUrl: data[k].skinUrl || `https://mc-heads.net/skin/${encodeURIComponent(data[k].ign)}`,
            model: data[k].model || "classic",
            accountType: data[k].accountType || "offline"
          };
        }
      }
    }
  } catch (e) {
    console.warn("RTDB getClaimedAccounts notice:", e);
  }

  // Also query Firestore subcollection
  try {
    const colRef = collection(db, "users", uid, "claimedAccounts");
    const snap = await getDocs(colRef);
    snap.forEach((d) => {
      const data = d.data();
      if (data?.ign && !accountsMap[data.ign.toLowerCase()]) {
        accountsMap[data.ign.toLowerCase()] = {
          ign: data.ign,
          skinUrl: data.skinUrl || `https://mc-heads.net/skin/${encodeURIComponent(data.ign)}`,
          model: data.model || "classic",
          accountType: data.accountType || "offline"
        };
      }
    });
  } catch (e) {
    console.warn("Firestore getClaimedAccounts notice:", e);
  }

  return Object.values(accountsMap);
}

/**
 * Deletes a claimed account from the user's roster.
 */
export async function deleteClaimedAccountFromCloud(
  uid: string,
  userEmail: string | null,
  ign: string
): Promise<void> {
  const cleanIgn = ign.trim();
  if (!cleanIgn) return;

  try {
    await deleteDoc(doc(db, "users", uid, "claimedAccounts", cleanIgn));
  } catch {}

  try {
    await remove(ref(rtdb, `users/${uid}/claimedAccounts/${cleanIgn}`));
  } catch {}

}
