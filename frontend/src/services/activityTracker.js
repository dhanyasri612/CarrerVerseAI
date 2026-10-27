/**
 * Daily & Monthly Activity / Streak Tracker Service for CareerVerse
 * Powers the LeetCode / GeeksforGeeks style monthly streak calendar,
 * habit streaks, daily completed milestones, DSA practice, and interview tracking.
 */

const STORAGE_KEY = "cv_user_daily_activities";

export function getLocalDateString(d = new Date()) {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/**
 * Reads recorded activity and removes demo records written by older versions.
 * Empty history stays empty; the dashboard must never imply practice happened
 * when the user did not record it.
 */
function getStoredActivities() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    const activities = parsed.filter(
      (activity) => !String(activity?.id || "").startsWith("seed_")
    );
    if (activities.length !== parsed.length) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(activities));
    }
    return activities;
  } catch (err) {
    console.warn("Failed to read recorded activities:", err);
    return [];
  }
}

/**
 * Record a new activity (e.g. from interview room, DSA studio, teaching studio).
 */
export function recordActivity({ type, title, detail, score = 1, date = null }) {
  try {
    const todayStr = date || getLocalDateString();
    const timestamp = new Date().toISOString();
    const existing = getStoredActivities();

    const newEntry = {
      id: `act_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      date: todayStr,
      timestamp,
      type, // 'interview' | 'dsa' | 'roadmap' | 'skill' | 'cert' | 'teaching'
      title,
      detail: detail || "",
      score,
    };

    const updated = [newEntry, ...existing];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));

    return newEntry;
  } catch (err) {
    console.warn("Failed to record activity:", err);
    return null;
  }
}

/**
 * Computes all-time streaks and active days from the activity dataset.
 */
export function computeGlobalStreaks(activities) {
  const activeDateSet = new Set(activities.map((a) => a.date));
  const sortedDates = Array.from(activeDateSet).sort();

  if (sortedDates.length === 0) {
    return { currentStreak: 0, maxStreak: 0, totalActiveDays: 0 };
  }

  // Calculate Max Streak across all dates
  let maxStreak = 0;
  let running = 0;
  let prevDate = null;

  for (const dateStr of sortedDates) {
    const curr = new Date(dateStr);
    if (!prevDate) {
      running = 1;
    } else {
      const diff = Math.round((curr - prevDate) / (1000 * 60 * 60 * 24));
      if (diff === 1) {
        running += 1;
      } else {
        running = 1;
      }
    }
    if (running > maxStreak) maxStreak = running;
    prevDate = curr;
  }

  // Calculate Current Streak backwards from today / yesterday
  const today = new Date();
  const todayStr = getLocalDateString(today);

  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  const yesterdayStr = getLocalDateString(yesterday);

  let currentStreak = 0;
  let checkDate = new Date();

  // If candidate has activity today, start checking from today; else if yesterday had activity, start from yesterday
  if (activeDateSet.has(todayStr)) {
    checkDate = new Date();
  } else if (activeDateSet.has(yesterdayStr)) {
    checkDate = new Date(yesterday);
  } else {
    return { currentStreak: 0, maxStreak, totalActiveDays: sortedDates.length };
  }

  while (true) {
    const dStr = getLocalDateString(checkDate);
    if (activeDateSet.has(dStr)) {
      currentStreak += 1;
      checkDate.setDate(checkDate.getDate() - 1);
    } else {
      break;
    }
  }

  return {
    currentStreak: Math.max(currentStreak, 1),
    maxStreak: Math.max(maxStreak, currentStreak),
    totalActiveDays: sortedDates.length,
  };
}

/**
 * Returns full monthly streak calendar data for any year and month (0-indexed month).
 * Exactly replicates the LeetCode / GeeksforGeeks monthly streak view!
 */
export function getMonthActivityMetrics(targetYear = null, targetMonth = null) {
  try {
    const activities = getStoredActivities();
    const now = new Date();

    const year = targetYear !== null ? targetYear : now.getFullYear();
    const month = targetMonth !== null ? targetMonth : now.getMonth(); // 0-indexed (0 = Jan, 9 = Oct)

    const todayStr = getLocalDateString(now);

    // Filter activities for this month
    const monthPrefix = `${year}-${String(month + 1).padStart(2, "0")}`;
    const monthActivities = activities.filter((a) => a.date && a.date.startsWith(monthPrefix));

    // Map by date for O(1) lookup
    const dateMap = new Map();
    monthActivities.forEach((act) => {
      if (!dateMap.has(act.date)) {
        dateMap.set(act.date, []);
      }
      dateMap.get(act.date).push(act);
    });

    const totalDaysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDayOfWeek = new Date(year, month, 1).getDay(); // 0 = Sun, 1 = Mon ... 6 = Sat

    const days = [];
    let activeDaysCount = 0;
    let totalProblemsCount = 0;

    for (let dayNum = 1; dayNum <= totalDaysInMonth; dayNum++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
      const dayActs = dateMap.get(dateStr) || [];
      const count = dayActs.length;
      const hasWork = count > 0;
      const isToday = dateStr === todayStr;
      const isFuture = dateStr > todayStr;

      if (hasWork) {
        activeDaysCount += 1;
        totalProblemsCount += count;
      }

      // Intensity level: 0 = Rest, 1 = Light (1-2), 2 = Steady (3-5), 3 = High (6+)
      let intensity = 0;
      if (count >= 6) intensity = 3;
      else if (count >= 3) intensity = 2;
      else if (count >= 1) intensity = 1;

      days.push({
        dayNumber: dayNum,
        date: dateStr,
        dayOfWeek: new Date(year, month, dayNum).getDay(),
        count,
        activities: dayActs,
        hasWork,
        isToday,
        isFuture,
        intensity,
      });
    }

    const { currentStreak, maxStreak, totalActiveDays } = computeGlobalStreaks(activities);

    // Calculate longest consecutive streak specifically within this month
    let monthMaxStreak = 0;
    let runningMonthStreak = 0;
    days.forEach((d) => {
      if (d.hasWork) {
        runningMonthStreak += 1;
        if (runningMonthStreak > monthMaxStreak) monthMaxStreak = runningMonthStreak;
      } else {
        runningMonthStreak = 0;
      }
    });

    const monthDateObj = new Date(year, month, 1);
    const monthName = monthDateObj.toLocaleDateString("en-US", { month: "long" });

    return {
      year,
      month,
      monthName,
      totalDaysInMonth,
      firstDayOfWeek, // padding slots before 1st of month
      days,
      activeDaysCount,
      totalProblemsCount,
      monthMaxStreak,
      currentStreak,
      maxStreak,
      totalActiveDays,
      completionRate: Math.round((activeDaysCount / totalDaysInMonth) * 100),
      isCurrentMonth: year === now.getFullYear() && month === now.getMonth(),
    };
  } catch (err) {
    console.error("Error computing month activity metrics:", err);
    return {
      year: new Date().getFullYear(),
      month: new Date().getMonth(),
      monthName: "Current Month",
      totalDaysInMonth: 31,
      firstDayOfWeek: 0,
      days: [],
      activeDaysCount: 0,
      totalProblemsCount: 0,
      monthMaxStreak: 0,
      currentStreak: 1,
      maxStreak: 1,
      totalActiveDays: 0,
      completionRate: 0,
      isCurrentMonth: true,
    };
  }
}

/**
 * Backward-compatible helper for 7-day overview & dashboard summaries.
 */
export function getActivityMetrics() {
  try {
    const activities = getStoredActivities();
    const todayStr = getLocalDateString();

    const todayActivities = activities.filter((a) => a.date === todayStr);

    // Calculate last 7 days distribution
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const dStr = getLocalDateString(d);
      const dayLabel = d.toLocaleDateString("en-US", { weekday: "short" });
      const count = activities.filter((a) => a.date === dStr).length;
      days.push({
        date: dStr,
        day: dayLabel,
        count,
        isToday: dStr === todayStr,
      });
    }

    const { currentStreak, maxStreak, totalActiveDays } = computeGlobalStreaks(activities);

    return {
      streak: currentStreak,
      maxStreak,
      totalActiveDays,
      todayCount: todayActivities.length,
      todayActivities,
      recentActivities: activities.slice(0, 10),
      last7Days: days,
      hasWorkToday: todayActivities.length > 0,
    };
  } catch (err) {
    return {
      streak: 0,
      maxStreak: 0,
      totalActiveDays: 0,
      todayCount: 0,
      todayActivities: [],
      recentActivities: [],
      last7Days: [],
      hasWorkToday: false,
    };
  }
}
