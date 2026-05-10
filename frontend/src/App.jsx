import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [filterDate, setFilterDate] = useState("");

  const fetchData = async () => {
    try {
      const sRes = await axios.get("http://127.0.0.1:8000/signal");
      const hRes = await axios.get("http://127.0.0.1:8000/history");
      setData(sRes.data);
      setHistory(hRes.data);
    } catch (e) { 
      console.error("API Error - Is your Python backend running?"); 
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 5000);
    return () => clearInterval(timer);
  }, []);

  if (!data) return <div style={styles.loading}>🚀 Booting AlphaBot...</div>;

  // Show only today's trades by default
  const todayStr = new Date().toLocaleDateString('en-CA'); 

  const filteredHistory = history.filter(h => {
    if (filterDate) {
      return h.time.startsWith(filterDate);
    }
    return h.time.startsWith(todayStr);
  });

  return (
    <div style={styles.fullPageCenter}>
      <div style={styles.card}>
        <h2 style={styles.title}>🚀 AlphaBot Pro Dashboard</h2>
        
        <div style={styles.tickBox}>
          <div style={styles.tick}>
            {"EMA (20 > 50):"} {data.ema20 > data.ema50 ? "✅" : "❌"}
            <span style={styles.smallVal}> ({data.ema20} vs {data.ema50})</span>
          </div>
          <div style={styles.tick}>
            {"RSI:"} <b>{data.rsi ? data.rsi.toFixed(1) : "—"}</b>
            <span style={styles.smallVal}>
              ({data.rsi > 70 ? "Overbought" : data.rsi < 30 ? "Oversold" : "Neutral"})
            </span>
          </div>
          <div style={styles.tick}>
            {"Volume Spike:"} {data.is_vol_spike ? "✅" : "❌"}
            <span style={styles.smallVal}> (Need &gt; Avg)</span>
          </div>
          
          <div style={styles.volumeDetails}>
            <div style={styles.volRow}>
                <span>Current Vol: <b>{data.current_vol?.toLocaleString()}</b></span>
                <span>Avg Vol: <b>{data.avg_vol?.toLocaleString()}</b></span>
            </div>
            <div style={styles.volTrack}>
                <div style={{
                    ...styles.volBar, 
                    width: `${Math.min((data.current_vol / data.avg_vol) * 100, 100)}%`,
                    backgroundColor: data.is_vol_spike ? "#2ecc71" : "#58a6ff"
                }}></div>
            </div>
          </div>
        </div>

        <div style={styles.priceRow}>
          <div style={styles.priceCol}>
            <span style={styles.priceLabel}>{data.stock} LIVE PRICE</span>
            <span style={styles.price}>₹{data.price}</span>
          </div>
          <span style={{
            ...styles.badge, 
            backgroundColor: data.signal === "BUY" ? "#2ecc71" : data.signal === "SELL" ? "#e74c3c" : "#444"
          }}>
            {data.signal}
          </span>
        </div>

        <div style={styles.historyHeader}>
          <h4 style={styles.logTitle}>📜 Signal History</h4>
          <input 
            type="date" 
            value={filterDate} 
            onChange={(e) => setFilterDate(e.target.value)} 
            style={styles.dateInput} 
          />
        </div>

        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr style={styles.th}>
                <th>Date & Time</th>
                <th>Signal</th>
                <th>Price</th>
                <th>Target</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.length === 0 ? (
                <tr><td colSpan="4" style={styles.noData}>No trades found for this date.</td></tr>
              ) : (
                filteredHistory.map((h, i) => {
                  const dateObj = new Date(h.time.replace(' ', 'T')); 
                  const displayTime = isNaN(dateObj) 
                    ? h.time 
                    : dateObj.toLocaleString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                      });

                  return (
                    <tr key={i} style={styles.tr}>
                      <td style={styles.td}>{displayTime}</td>
                      <td style={{color: h.type === "BUY" ? "#2ecc71" : "#e74c3c", fontWeight: "bold", padding: "10px"}}>
                        {h.type}
                      </td>
                      <td style={styles.td}>₹{h.price}</td>
                      <td style={styles.td}>₹{h.target}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        <div style={styles.footer}>
          Last Update: {data.last_updated} | Status: {data.market_status}
        </div>
      </div>
    </div>
  );
}

const styles = {
  fullPageCenter: { display: "flex", justifyContent: "center", alignItems: "center", width: "100vw", height: "100vh", backgroundColor: "#0d1117", color: "white", fontFamily: "sans-serif", margin: 0, padding: 0, overflow: "hidden" },
  card: { backgroundColor: "#161b22", padding: "35px", borderRadius: "24px", width: "100%", maxWidth: "600px", border: "1px solid #30363d" },
  title: { textAlign: "center", marginBottom: "30px", color: "#58a6ff" },
  tickBox: { display: "flex", flexDirection: "column", gap: "12px", backgroundColor: "#0d1117", padding: "20px", borderRadius: "15px", marginBottom: "25px" },
  tick: { fontSize: "14px", display: "flex", justifyContent: "space-between" },
  smallVal: { color: "#8b949e", fontSize: "12px" },
  volumeDetails: { marginTop: "5px", padding: "10px", backgroundColor: "#1c2128", borderRadius: "8px" },
  volRow: { display: "flex", justifyContent: "space-between", fontSize: "11px", marginBottom: "8px" },
  volTrack: { height: "6px", backgroundColor: "#30363d", borderRadius: "3px", overflow: "hidden" },
  volBar: { height: "100%", transition: "width 0.5s ease-in-out" },
  priceRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" },
  priceCol: { display: "flex", flexDirection: "column" },
  priceLabel: { fontSize: "11px", color: "#8b949e" },
  price: { fontSize: "44px", fontWeight: "bold" },
  badge: { padding: "10px 25px", borderRadius: "12px", color: "white", fontWeight: "bold" },
  historyHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" },
  logTitle: { margin: 0, color: "#58a6ff" },
  dateInput: { backgroundColor: "#21262d", color: "white", border: "1px solid #30363d", padding: "8px", borderRadius: "6px" },
  tableContainer: { maxHeight: "200px", overflowY: "auto", border: "1px solid #30363d", borderRadius: "10px" },
  table: { width: "100%", borderCollapse: "collapse" },
  th: { backgroundColor: "#21262d", color: "#8b949e", textAlign: "left", padding: "12px" },
  tr: { borderBottom: "1px solid #30363d", height: "45px" },
  td: { padding: "10px", whiteSpace: "nowrap" },
  noData: { textAlign: "center", padding: "30px", color: "#484f58" },
  footer: { marginTop: "20px", fontSize: "11px", color: "#8b949e", textAlign: "center" },
  loading: { height: "100vh", display: "flex", justifyContent: "center", alignItems: "center", color: "#58a6ff" }
};

export default App;
// import React, { useEffect, useState } from "react";
// import axios from "axios";

// function App() {
//   const [data, setData] = useState(null);
//   const [history, setHistory] = useState([]);
//   const [filterDate, setFilterDate] = useState("");

//   const fetchData = async () => {
//     try {
//       const sRes = await axios.get("http://127.0.0.1:8000/signal");
//       const hRes = await axios.get("http://127.0.0.1:8000/history");
//       setData(sRes.data);
//       setHistory(hRes.data);
//     } catch (e) { 
//       console.error("API Error - Is your Python backend running?"); 
//     }
//   };

//   useEffect(() => {
//     fetchData();
//     const timer = setInterval(fetchData, 5000);
//     return () => clearInterval(timer);
//   }, []);

//   if (!data) return <div style={styles.loading}>🚀 Booting AlphaBot...</div>;

//   // Show only today's trades by default
//   const todayStr = new Date().toLocaleDateString('en-CA'); 

//   const filteredHistory = history.filter(h => {
//     if (filterDate) {
//       return h.time.startsWith(filterDate);
//     }
//     return h.time.startsWith(todayStr);
//   });

//   return (
//     <div style={styles.fullPageCenter}>
//       <div style={styles.card}>
//         <h2 style={styles.title}>🚀 AlphaBot Pro Dashboard</h2>
        
//         <div style={styles.tickBox}>
//           <div style={styles.tick}>
//             {"EMA (20 > 50):"} {data.ema20 > data.ema50 ? "✅" : "❌"}
//             <span style={styles.smallVal}> ({data.ema20} vs {data.ema50})</span>
//           </div>
//           <div style={styles.tick}>
//             {"RSI:"} <b>{data.rsi ? data.rsi.toFixed(1) : "—"}</b>
//             <span style={styles.smallVal}>
//               ({data.rsi > 70 ? "Overbought" : data.rsi < 30 ? "Oversold" : "Neutral"})
//             </span>
//           </div>
//           <div style={styles.tick}>
//             {"Volume Spike:"} {data.is_vol_spike ? "✅" : "❌"}
//             <span style={styles.smallVal}> (Need &gt; Avg)</span>
//           </div>
          
//           <div style={styles.volumeDetails}>
//             <div style={styles.volRow}>
//                 <span>Current Vol: <b>{data.current_vol?.toLocaleString()}</b></span>
//                 <span>Avg Vol: <b>{data.avg_vol?.toLocaleString()}</b></span>
//             </div>
//             <div style={styles.volTrack}>
//                 <div style={{
//                     ...styles.volBar, 
//                     width: `${Math.min((data.current_vol / data.avg_vol) * 100, 100)}%`,
//                     backgroundColor: data.is_vol_spike ? "#2ecc71" : "#58a6ff"
//                 }}></div>
//             </div>
//           </div>
//         </div>

//         <div style={styles.priceRow}>
//           <div style={styles.priceCol}>
//             <span style={styles.priceLabel}>{data.stock} LIVE PRICE</span>
//             <span style={styles.price}>₹{data.price}</span>
//           </div>
//           <span style={{
//             ...styles.badge, 
//             backgroundColor: data.signal === "BUY" ? "#2ecc71" : data.signal === "SELL" ? "#e74c3c" : "#444"
//           }}>
//             {data.signal}
//           </span>
//         </div>

//         <div style={styles.historyHeader}>
//           <h4 style={styles.logTitle}>📜 Signal History</h4>
//           <input 
//             type="date" 
//             value={filterDate} 
//             onChange={(e) => setFilterDate(e.target.value)} 
//             style={styles.dateInput} 
//           />
//         </div>

//         <div style={styles.tableContainer}>
//           <table style={styles.table}>
//             <thead>
//               <tr style={styles.th}>
//                 <th>Date & Time</th>
//                 <th>Signal</th>
//                 <th>Price</th>
//                 <th>Target</th>
//               </tr>
//             </thead>
//             <tbody>
//               {filteredHistory.length === 0 ? (
//                 <tr><td colSpan="4" style={styles.noData}>No trades found for this date.</td></tr>
//               ) : (
//                 filteredHistory.map((h, i) => {
//                   const dateObj = new Date(h.time.replace(' ', 'T')); 
//                   const displayTime = isNaN(dateObj) 
//                     ? h.time 
//                     : dateObj.toLocaleString('en-IN', {
//                         day: '2-digit',
//                         month: 'short',
//                         hour: '2-digit',
//                         minute: '2-digit',
//                         hour12: false
//                       });

//                   return (
//                     <tr key={i} style={styles.tr}>
//                       <td style={styles.td}>{displayTime}</td>
//                       <td style={{color: h.type === "BUY" ? "#2ecc71" : "#e74c3c", fontWeight: "bold", padding: "10px"}}>
//                         {h.type}
//                       </td>
//                       <td style={styles.td}>₹{h.price}</td>
//                       <td style={styles.td}>₹{h.target}</td>
//                     </tr>
//                   );
//                 })
//               )}
//             </tbody>
//           </table>
//         </div>

//         <div style={styles.footer}>
//           Last Update: {data.last_updated} | Status: {data.market_status}
//         </div>
//       </div>
//     </div>
//   );
// }

// const styles = {
//   fullPageCenter: { display: "flex", justifyContent: "center", alignItems: "center", width: "100vw", height: "100vh", backgroundColor: "#0d1117", color: "white", fontFamily: "sans-serif", margin: 0, padding: 0, overflow: "hidden" },
//   card: { backgroundColor: "#161b22", padding: "35px", borderRadius: "24px", width: "100%", maxWidth: "600px", border: "1px solid #30363d" },
//   title: { textAlign: "center", marginBottom: "30px", color: "#58a6ff" },
//   tickBox: { display: "flex", flexDirection: "column", gap: "12px", backgroundColor: "#0d1117", padding: "20px", borderRadius: "15px", marginBottom: "25px" },
//   tick: { fontSize: "14px", display: "flex", justifyContent: "space-between" },
//   smallVal: { color: "#8b949e", fontSize: "12px" },
//   volumeDetails: { marginTop: "5px", padding: "10px", backgroundColor: "#1c2128", borderRadius: "8px" },
//   volRow: { display: "flex", justifyContent: "space-between", fontSize: "11px", marginBottom: "8px" },
//   volTrack: { height: "6px", backgroundColor: "#30363d", borderRadius: "3px", overflow: "hidden" },
//   volBar: { height: "100%", transition: "width 0.5s ease-in-out" },
//   priceRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" },
//   priceCol: { display: "flex", flexDirection: "column" },
//   priceLabel: { fontSize: "11px", color: "#8b949e" },
//   price: { fontSize: "44px", fontWeight: "bold" },
//   badge: { padding: "10px 25px", borderRadius: "12px", color: "white", fontWeight: "bold" },
//   historyHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" },
//   logTitle: { margin: 0, color: "#58a6ff" },
//   dateInput: { backgroundColor: "#21262d", color: "white", border: "1px solid #30363d", padding: "8px", borderRadius: "6px" },
//   tableContainer: { maxHeight: "200px", overflowY: "auto", border: "1px solid #30363d", borderRadius: "10px" },
//   table: { width: "100%", borderCollapse: "collapse" },
//   th: { backgroundColor: "#21262d", color: "#8b949e", textAlign: "left", padding: "12px" },
//   tr: { borderBottom: "1px solid #30363d", height: "45px" },
//   td: { padding: "10px", whiteSpace: "nowrap" },
//   noData: { textAlign: "center", padding: "30px", color: "#484f58" },
//   footer: { marginTop: "20px", fontSize: "11px", color: "#8b949e", textAlign: "center" },
//   loading: { height: "100vh", display: "flex", justifyContent: "center", alignItems: "center", color: "#58a6ff" }
// };

// export default App;
// import React, { useEffect, useState } from "react";
// import axios from "axios";

// function App() {
//   const [data, setData] = useState(null);
//   const [history, setHistory] = useState([]);
//   const [filterDate, setFilterDate] = useState("");

//   const fetchData = async () => {
//     try {
//       const sRes = await axios.get("http://127.0.0.1:8000/signal");
//       const hRes = await axios.get("http://127.0.0.1:8000/history");
//       setData(sRes.data);
//       setHistory(hRes.data);
//     } catch (e) { 
//       console.error("API Error - Is your Python backend running?"); 
//     }
//   };

//   useEffect(() => {
//     fetchData();
//     const timer = setInterval(fetchData, 5000);
//     return () => clearInterval(timer);
//   }, []);

//   if (!data) return <div style={styles.loading}>🚀 Booting AlphaBot...</div>;

//   // IMPROVED FILTER: Checks if the selected date string is found anywhere in the trade time
//   const filteredHistory = filterDate 
//     ? history.filter(h => h.time.includes(filterDate)) 
//     : history;

//   return (
//     <div style={styles.fullPageCenter}>
//       <div style={styles.card}>
//         <h2 style={styles.title}>🚀 AlphaBot Pro Dashboard</h2>
        
//         <div style={styles.tickBox}>
//           <div style={styles.tick}>
//             {"EMA (20 > 50):"} {data.ema20 > data.ema50 ? "✅" : "❌"}
//             <span style={styles.smallVal}> ({data.ema20} vs {data.ema50})</span>
//           </div>
//           <div style={styles.tick}>
//             {"Volume Spike:"} {data.is_vol_spike ? "✅" : "❌"}
//             <span style={styles.smallVal}> {"(Need > Avg)"}</span>
//           </div>
          
//           <div style={styles.volumeDetails}>
//             <div style={styles.volRow}>
//                 <span>Current Vol: <b>{data.current_vol?.toLocaleString()}</b></span>
//                 <span>Avg Vol: <b>{data.avg_vol?.toLocaleString()}</b></span>
//             </div>
//             <div style={styles.volTrack}>
//                 <div style={{
//                     ...styles.volBar, 
//                     width: `${Math.min((data.current_vol / data.avg_vol) * 100, 100)}%`,
//                     backgroundColor: data.is_vol_spike ? "#2ecc71" : "#58a6ff"
//                 }}></div>
//             </div>
//           </div>
//         </div>

//         <div style={styles.priceRow}>
//           <div style={styles.priceCol}>
//             <span style={styles.priceLabel}>{data.stock} LIVE PRICE</span>
//             <span style={styles.price}>₹{data.price}</span>
//           </div>
//           <span style={{
//             ...styles.badge, 
//             backgroundColor: data.signal === "BUY" ? "#2ecc71" : data.signal === "SELL" ? "#e74c3c" : "#444"
//           }}>
//             {data.signal}
//           </span>
//         </div>

//         <div style={styles.historyHeader}>
//           <h4 style={styles.logTitle}>📜 Signal History</h4>
//           <input 
//             type="date" 
//             value={filterDate} 
//             onChange={(e) => setFilterDate(e.target.value)} 
//             style={styles.dateInput} 
//           />
//         </div>

//         <div style={styles.tableContainer}>
//           <table style={styles.table}>
//             <thead>
//               <tr style={styles.th}>
//                 <th>Date & Time</th>
//                 <th>Signal</th>
//                 <th>Price</th>
//                 <th>Target</th>
//               </tr>
//             </thead>
//             <tbody>
//               {filteredHistory.length === 0 ? (
//                 <tr><td colSpan="4" style={styles.noData}>No trades found for this date.</td></tr>
//               ) : (
//                 filteredHistory.map((h, i) => {
//                   // FORMATTING THE DATE: Turns "2026-01-16 13:18" into "16 Jan, 13:18"
//                   const dateObj = new Date(h.time.replace(' ', 'T')); 
//                   const displayTime = isNaN(dateObj) 
//                     ? h.time // Fallback if time isn't a valid date
//                     : dateObj.toLocaleString('en-IN', {
//                         day: '2-digit',
//                         month: 'short',
//                         hour: '2-digit',
//                         minute: '2-digit',
//                         hour12: false
//                       });

//                   return (
//                     <tr key={i} style={styles.tr}>
//                       <td style={styles.td}>{displayTime}</td>
//                       <td style={{color: h.type === "BUY" ? "#2ecc71" : "#e74c3c", fontWeight: "bold", padding: "10px"}}>
//                         {h.type}
//                       </td>
//                       <td style={styles.td}>₹{h.price}</td>
//                       <td style={styles.td}>₹{h.target}</td>
//                     </tr>
//                   );
//                 })
//               )}
//             </tbody>
//           </table>
//         </div>

//         <div style={styles.footer}>
//           Last Update: {data.last_updated} | Status: {data.market_status}
//         </div>
//       </div>
//     </div>
//   );
// }

// const styles = {
//   fullPageCenter: { display: "flex", justifyContent: "center", alignItems: "center", width: "100vw", height: "100vh", backgroundColor: "#0d1117", color: "white", fontFamily: "sans-serif", margin: 0, padding: 0, overflow: "hidden" },
//   card: { backgroundColor: "#161b22", padding: "35px", borderRadius: "24px", width: "100%", maxWidth: "600px", border: "1px solid #30363d" },
//   title: { textAlign: "center", marginBottom: "30px", color: "#58a6ff" },
//   tickBox: { display: "flex", flexDirection: "column", gap: "12px", backgroundColor: "#0d1117", padding: "20px", borderRadius: "15px", marginBottom: "25px" },
//   tick: { fontSize: "14px", display: "flex", justifyContent: "space-between" },
//   smallVal: { color: "#8b949e", fontSize: "12px" },
//   volumeDetails: { marginTop: "5px", padding: "10px", backgroundColor: "#1c2128", borderRadius: "8px" },
//   volRow: { display: "flex", justifyContent: "space-between", fontSize: "11px", marginBottom: "8px" },
//   volTrack: { height: "6px", backgroundColor: "#30363d", borderRadius: "3px", overflow: "hidden" },
//   volBar: { height: "100%", transition: "width 0.5s ease-in-out" },
//   priceRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" },
//   priceCol: { display: "flex", flexDirection: "column" },
//   priceLabel: { fontSize: "11px", color: "#8b949e" },
//   price: { fontSize: "44px", fontWeight: "bold" },
//   badge: { padding: "10px 25px", borderRadius: "12px", color: "white", fontWeight: "bold" },
//   historyHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" },
//   logTitle: { margin: 0, color: "#58a6ff" },
//   dateInput: { backgroundColor: "#21262d", color: "white", border: "1px solid #30363d", padding: "8px", borderRadius: "6px" },
//   tableContainer: { maxHeight: "200px", overflowY: "auto", border: "1px solid #30363d", borderRadius: "10px" },
//   table: { width: "100%", borderCollapse: "collapse" },
//   th: { backgroundColor: "#21262d", color: "#8b949e", textAlign: "left", padding: "12px" },
//   tr: { borderBottom: "1px solid #30363d", height: "45px" },
//   td: { padding: "10px", whiteSpace: "nowrap" },
//   noData: { textAlign: "center", padding: "30px", color: "#484f58" },
//   footer: { marginTop: "20px", fontSize: "11px", color: "#8b949e", textAlign: "center" },
//   loading: { height: "100vh", display: "flex", justifyContent: "center", alignItems: "center", color: "#58a6ff" }
// };

// export default App;