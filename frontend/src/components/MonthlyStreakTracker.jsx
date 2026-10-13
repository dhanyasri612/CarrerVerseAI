import React, { useState, useMemo } from "react";
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Flame,
  Zap,
  CheckCircle2,
  Trophy,
  Target,
  Sparkles,
  Info,
  Clock,
  Code2,
  Brain,
  RotateCcw,
} from "lucide-react";
import { getMonthActivityMetrics, getLocalDateString } from "../services/activityTracker";

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function MonthlyStreakTracker({ onOpenDsaModal }) {
  const today = useMemo(() => new Date(), []);
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(today.getMonth()); // 0-indexed
  const [selectedDay, setSelectedDay] = useState(null);

  // Compute metrics for the selected year & month
  const metrics = useMemo(() => {
    return getMonthActivityMetrics(currentYear, currentMonth);
  }, [currentYear, currentMonth]);

  // Navigate to previous month
  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear((prev) => prev - 1);
    } else {
      setCurrentMonth((prev) => prev - 1);
    }
    setSelectedDay(null);
  };

  // Navigate to next month
  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear((prev) => prev + 1);
    } else {
      setCurrentMonth((prev) => prev + 1);
    }
    setSelectedDay(null);
  };

  // Jump to today's month
  const handleJumpToCurrent = () => {
    setCurrentYear(today.getFullYear());
    setCurrentMonth(today.getMonth());
    setSelectedDay(null);
  };

  const isCurrentMonthView =
    currentYear === today.getFullYear() && currentMonth === today.getMonth();

  // Highlight color & intensity styling matching LeetCode & GeeksforGeeks
  const getIntensityStyles = (intensity, hasWork, isToday, isFuture, isSelected) => {
    if (isFuture) {
      return {
        bg: "#f8fafc",
        border: "1px dashed #cbd5e1",
        color: "#94a3b8",
        badgeBg: "transparent",
        badgeText: "#94a3b8",
        opacity: 0.55,
      };
    }

    if (!hasWork) {
      return {
        bg: isSelected ? "#f1f5f9" : "#f8fafc",
        border: isSelected ? "2px solid #94a3b8" : "1px solid #e2e8f0",
        color: "#64748b",
        badgeBg: "#f1f5f9",
        badgeText: "#94a3b8",
        opacity: 1,
      };
    }

    // Active intensities
    switch (intensity) {
      case 3: // 6+ problems (Intense / LeetCode Green 🔥)
        return {
          bg: isSelected ? "#15803d" : "#22c55e",
          border: isSelected ? "2px solid #0f172a" : "1px solid #16a34a",
          color: "#ffffff",
          badgeBg: "rgba(255, 255, 255, 0.25)",
          badgeText: "#ffffff",
          shadow: "0 2px 8px rgba(34, 197, 94, 0.35)",
          opacity: 1,
        };
      case 2: // 3-5 problems (Steady)
        return {
          bg: isSelected ? "#4ade80" : "#86efac",
          border: isSelected ? "2px solid #15803d" : "1px solid #4ade80",
          color: "#065f46",
          badgeBg: "rgba(6, 95, 70, 0.12)",
          badgeText: "#065f46",
          shadow: "0 2px 6px rgba(134, 239, 172, 0.25)",
          opacity: 1,
        };
      case 1: // 1-2 problems (Light)
      default:
        return {
          bg: isSelected ? "#bbf7d0" : "#dcfce7",
          border: isSelected ? "2px solid #16a34a" : "1px solid #86efac",
          color: "#166534",
          badgeBg: "rgba(22, 101, 52, 0.1)",
          badgeText: "#166534",
          shadow: "none",
          opacity: 1,
        };
    }
  };

  return (
    <div
      style={{
        background: "#ffffff",
        border: "1px solid var(--cv-rule, #e2e8f0)",
        borderRadius: "16px",
        padding: "1.5rem",
        marginBottom: "1.75rem",
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.03)",
      }}
    >
      {/* Top Header Bar: Title, Month Navigator & Jump to Today */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "1rem",
          marginBottom: "1.25rem",
          paddingBottom: "1rem",
          borderBottom: "1px solid #f1f5f9",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "#eff6ff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#2563eb",
            }}
          >
            <CalendarIcon size={20} />
          </div>
          <div>
            <h3
              style={{
                margin: 0,
                fontSize: "1.1rem",
                fontWeight: 800,
                color: "#0f172a",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              Monthly Consistency Tracker
              <span
                style={{
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  background: "#dcfce7",
                  color: "#15803d",
                  padding: "2px 8px",
                  borderRadius: "20px",
                  border: "1px solid #86efac",
                }}
              >
                LeetCode & GFG Style
              </span>
            </h3>
            <p style={{ margin: "2px 0 0 0", fontSize: "0.8rem", color: "#64748b" }}>
              Solve problems and complete mock interviews every day to build your streak.
            </p>
          </div>
        </div>

        {/* Month Navigation Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {!isCurrentMonthView && (
            <button
              onClick={handleJumpToCurrent}
              title="Jump to current month"
              style={{
                display: "flex",
                alignItems: "center",
                gap: "5px",
                background: "#f8fafc",
                border: "1px solid #cbd5e1",
                padding: "6px 12px",
                borderRadius: "8px",
                fontSize: "0.78rem",
                fontWeight: 600,
                color: "#334155",
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              <RotateCcw size={13} /> Current Month
            </button>
          )}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
              borderRadius: "10px",
              padding: "3px",
            }}
          >
            <button
              onClick={handlePrevMonth}
              title="Previous Month"
              aria-label="Previous Month"
              style={{
                background: "transparent",
                border: "none",
                padding: "6px 8px",
                borderRadius: "6px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                color: "#475569",
              }}
            >
              <ChevronLeft size={18} />
            </button>

            <span
              style={{
                padding: "0 12px",
                fontWeight: 800,
                fontSize: "0.95rem",
                color: "#0f172a",
                minWidth: "140px",
                textAlign: "center",
              }}
            >
              {MONTH_NAMES[currentMonth]} {currentYear}
            </span>

            <button
              onClick={handleNextMonth}
              title="Next Month"
              aria-label="Next Month"
              style={{
                background: "transparent",
                border: "none",
                padding: "6px 8px",
                borderRadius: "6px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                color: "#475569",
              }}
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* LeetCode & GFG Streak Summary Badges Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "10px",
          marginBottom: "1.5rem",
        }}
      >
        {/* Current Active Streak */}
        <div
          style={{
            background: "#fff7ed",
            border: "1px solid #fed7aa",
            borderRadius: "12px",
            padding: "10px 14px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "#ffedd5",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#ea580c",
            }}
          >
            <Flame size={20} />
          </div>
          <div>
            <div style={{ fontSize: "0.72rem", color: "#9a3412", fontWeight: 700, textTransform: "uppercase" }}>
              Current Streak
            </div>
            <div style={{ fontSize: "1.15rem", fontWeight: 900, color: "#c2410c" }}>
              {metrics.currentStreak} {metrics.currentStreak === 1 ? "Day" : "Days"} 🔥
            </div>
          </div>
        </div>

        {/* Longest / Max Streak */}
        <div
          style={{
            background: "#fefce8",
            border: "1px solid #fef08a",
            borderRadius: "12px",
            padding: "10px 14px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "#fef9c3",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#ca8a04",
            }}
          >
            <Zap size={20} />
          </div>
          <div>
            <div style={{ fontSize: "0.72rem", color: "#854d0e", fontWeight: 700, textTransform: "uppercase" }}>
              Max Streak
            </div>
            <div style={{ fontSize: "1.15rem", fontWeight: 900, color: "#a16207" }}>
              {metrics.maxStreak} Days ⚡
            </div>
          </div>
        </div>

        {/* Active Days this Month */}
        <div
          style={{
            background: "#f0fdf4",
            border: "1px solid #bbf7d0",
            borderRadius: "12px",
            padding: "10px 14px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "#dcfce7",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#16a34a",
            }}
          >
            <CheckCircle2 size={20} />
          </div>
          <div>
            <div style={{ fontSize: "0.72rem", color: "#166534", fontWeight: 700, textTransform: "uppercase" }}>
              Active in {MONTH_NAMES[currentMonth].slice(0, 3)}
            </div>
            <div style={{ fontSize: "1.15rem", fontWeight: 900, color: "#15803d" }}>
              {metrics.activeDaysCount} / {metrics.totalDaysInMonth} Days
            </div>
          </div>
        </div>

        {/* Total Month Problems / Submissions */}
        <div
          style={{
            background: "#f5f3ff",
            border: "1px solid #ddd6fe",
            borderRadius: "12px",
            padding: "10px 14px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "#ede9fe",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#7c3aed",
            }}
          >
            <Target size={20} />
          </div>
          <div>
            <div style={{ fontSize: "0.72rem", color: "#5b21b6", fontWeight: 700, textTransform: "uppercase" }}>
              Total Activities
            </div>
            <div style={{ fontSize: "1.15rem", fontWeight: 900, color: "#6d28d9" }}>
              {metrics.totalProblemsCount} Solved 🎯
            </div>
          </div>
        </div>
      </div>

      {/* Weekday Headers (Sun - Sat) */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(7, 1fr)",
          gap: "8px",
          textAlign: "center",
          marginBottom: "8px",
        }}
      >
        {WEEKDAYS.map((dayName, idx) => (
          <div
            key={dayName}
            style={{
              fontSize: "0.76rem",
              fontWeight: 700,
              color: idx === 0 || idx === 6 ? "#94a3b8" : "#64748b",
              textTransform: "uppercase",
              letterSpacing: "0.04em",
              padding: "4px 0",
            }}
          >
            {dayName}
          </div>
        ))}
      </div>

      {/* Calendar Matrix Grid (Empty Offset Padding + 1..31 Days) */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(7, 1fr)",
          gap: "8px",
          marginBottom: "1.25rem",
        }}
      >
        {/* Leading empty padding slots */}
        {Array.from({ length: metrics.firstDayOfWeek }).map((_, padIdx) => (
          <div
            key={`pad_${padIdx}`}
            style={{
              background: "transparent",
              border: "1px dashed transparent",
              borderRadius: "10px",
              minHeight: "68px",
            }}
          />
        ))}

        {/* Month Day Cells */}
        {metrics.days.map((dayItem) => {
          const isSelected = selectedDay && selectedDay.date === dayItem.date;
          const styles = getIntensityStyles(
            dayItem.intensity,
            dayItem.hasWork,
            dayItem.isToday,
            dayItem.isFuture,
            isSelected
          );

          return (
            <div
              key={dayItem.date}
              onClick={() => {
                if (!dayItem.isFuture) {
                  setSelectedDay(isSelected ? null : dayItem);
                }
              }}
              title={`${dayItem.date}: ${
                dayItem.hasWork
                  ? `${dayItem.count} activities completed`
                  : dayItem.isFuture
                  ? "Upcoming"
                  : "Rest day (0 activities)"
              }`}
              style={{
                position: "relative",
                background: styles.bg,
                border: styles.border,
                borderRadius: "12px",
                padding: "8px 6px",
                minHeight: "72px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: dayItem.isFuture ? "default" : "pointer",
                transition: "all 0.15s ease",
                opacity: styles.opacity,
                boxShadow: styles.shadow || (isSelected ? "0 0 0 3px rgba(37, 99, 235, 0.2)" : "none"),
                transform: isSelected ? "scale(1.02)" : "none",
              }}
            >
              {/* Day Header: Day Number + Today Badge */}
              <div
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0 2px",
                }}
              >
                <span
                  style={{
                    fontSize: "0.78rem",
                    fontWeight: 700,
                    color: styles.color,
                  }}
                >
                  {dayItem.dayNumber}
                </span>

                {dayItem.isToday && (
                  <span
                    style={{
                      fontSize: "0.6rem",
                      fontWeight: 800,
                      background: "#f59e0b",
                      color: "#ffffff",
                      padding: "1px 4px",
                      borderRadius: "6px",
                      textTransform: "uppercase",
                      letterSpacing: "0.02em",
                    }}
                  >
                    Today
                  </span>
                )}
              </div>

              {/* Main Center Stat: Count of problems solved */}
              <div
                style={{
                  fontSize: "1.15rem",
                  fontWeight: 900,
                  color: styles.color,
                  margin: "2px 0",
                  display: "flex",
                  alignItems: "center",
                  gap: "2px",
                }}
              >
                {dayItem.count}
                {dayItem.intensity === 3 && <Flame size={14} color="#ffffff" />}
              </div>

              {/* Status Badge: "Done ✓", "Rest", or "Upcoming" */}
              <div
                style={{
                  fontSize: "0.66rem",
                  fontWeight: 700,
                  padding: "1px 6px",
                  borderRadius: "6px",
                  background: styles.badgeBg,
                  color: styles.badgeText,
                  textAlign: "center",
                  whiteSpace: "nowrap",
                }}
              >
                {dayItem.isFuture
                  ? "Future"
                  : dayItem.hasWork
                  ? "Done ✓"
                  : "Rest"}
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Day Details Drawer / Interactive Modal Card */}
      {selectedDay && (
        <div
          style={{
            background: "#f8fafc",
            border: "1px solid #cbd5e1",
            borderRadius: "12px",
            padding: "1rem 1.25rem",
            marginBottom: "1.25rem",
            animation: "fadeIn 0.2s ease-in-out",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "0.92rem", fontWeight: 800, color: "#0f172a" }}>
                {new Date(selectedDay.date + "T00:00:00").toLocaleDateString("en-US", {
                  weekday: "long",
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </span>
              <span
                style={{
                  background: selectedDay.hasWork ? "#dcfce7" : "#e2e8f0",
                  color: selectedDay.hasWork ? "#15803d" : "#475569",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  padding: "2px 8px",
                  borderRadius: "12px",
                  border: `1px solid ${selectedDay.hasWork ? "#86efac" : "#cbd5e1"}`,
                }}
              >
                {selectedDay.count} {selectedDay.count === 1 ? "Activity" : "Activities"}
              </span>
            </div>
            <button
              onClick={() => setSelectedDay(null)}
              style={{
                background: "transparent",
                border: "none",
                fontSize: "0.78rem",
                color: "#64748b",
                cursor: "pointer",
                fontWeight: 600,
              }}
            >
              ✕ Close
            </button>
          </div>

          {selectedDay.hasWork ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {selectedDay.activities.map((act, aIdx) => (
                <div
                  key={act.id || aIdx}
                  style={{
                    background: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    {act.type === "dsa" ? (
                      <Code2 size={16} color="#0284c7" />
                    ) : act.type === "interview" ? (
                      <Brain size={16} color="#7c3aed" />
                    ) : (
                      <CheckCircle2 size={16} color="#16a34a" />
                    )}
                    <div>
                      <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "#1e293b" }}>
                        {act.title}
                      </div>
                      {act.detail && (
                        <div style={{ fontSize: "0.72rem", color: "#64748b" }}>
                          {act.detail}
                        </div>
                      )}
                    </div>
                  </div>
                  <span
                    style={{
                      fontSize: "0.68rem",
                      fontWeight: 700,
                      color: "#15803d",
                      background: "#dcfce7",
                      padding: "2px 6px",
                      borderRadius: "6px",
                    }}
                  >
                    Verified ✓
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "10px",
                padding: "8px 0",
              }}
            >
              <div style={{ fontSize: "0.82rem", color: "#64748b" }}>
                No practice logged on this day. Complete a daily problem or interview to light up this day!
              </div>
              {onOpenDsaModal && (
                <button
                  onClick={onOpenDsaModal}
                  style={{
                    background: "#2563eb",
                    color: "#ffffff",
                    border: "none",
                    padding: "6px 14px",
                    borderRadius: "8px",
                    fontSize: "0.8rem",
                    fontWeight: 700,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <Code2 size={14} /> Practice Problem of the Day
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Legend & Motivation Footer */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "12px",
          paddingTop: "0.75rem",
          borderTop: "1px solid #f1f5f9",
          fontSize: "0.75rem",
          color: "#64748b",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span>Intensity:</span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span
              style={{
                display: "inline-block",
                width: "12px",
                height: "12px",
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                borderRadius: "3px",
              }}
            />
            <span>0 (Rest)</span>
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span
              style={{
                display: "inline-block",
                width: "12px",
                height: "12px",
                background: "#dcfce7",
                border: "1px solid #86efac",
                borderRadius: "3px",
              }}
            />
            <span>1-2 (Light)</span>
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span
              style={{
                display: "inline-block",
                width: "12px",
                height: "12px",
                background: "#86efac",
                border: "1px solid #4ade80",
                borderRadius: "3px",
              }}
            />
            <span>3-5 (Steady)</span>
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span
              style={{
                display: "inline-block",
                width: "12px",
                height: "12px",
                background: "#22c55e",
                border: "1px solid #16a34a",
                borderRadius: "3px",
              }}
            />
            <span>6+ (Master) 🔥</span>
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "6px", fontStyle: "italic" }}>
          <Sparkles size={13} color="#f59e0b" />
          <span>"Consistent daily practice compounds into offer letters."</span>
        </div>
      </div>
    </div>
  );
}
