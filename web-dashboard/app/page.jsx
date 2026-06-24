"use client";

import { useState, useEffect } from "react";
import { FaPaperPlane, FaSearch, FaCheck, FaExclamationTriangle, FaEnvelope, FaExternalLinkAlt, FaSync, FaPhone, FaArchive, FaList, FaTimes } from "react-icons/fa";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("new"); // "new" oder "archive"
  const [contactFilter, setContactFilter] = useState("all");

  const fetchLocalLeads = async () => {
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const res = await fetch("/api/local-leads");
      if (!res.ok) {
        throw new Error("Failed to fetch local leads");
      }
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      
      let fetchedLeads = data.leads || [];
      
      // Sortieren: Niedrige Punktzahl (Guter Lead für uns) nach oben.
      // Keine Website ganz nach oben.
      fetchedLeads.sort((a, b) => {
        const scoreA = parseInt(a['Performance Score']);
        const scoreB = parseInt(b['Performance Score']);
        
        const hasScoreA = !isNaN(scoreA);
        const hasScoreB = !isNaN(scoreB);
        
        const noWebA = !a.Website || a.Website === "None";
        const noWebB = !b.Website || b.Website === "None";

        // 1. Keine Website ganz nach oben
        if (noWebA && !noWebB) return -1;
        if (!noWebA && noWebB) return 1;

        // 2. Niedrigster Score (schlechte Website = super Lead) zuerst
        if (hasScoreA && hasScoreB) return scoreA - scoreB;
        
        // 3. Fallback: Firmen mit Score über Firmen ohne Score/Website
        if (hasScoreA && !hasScoreB) return -1;
        if (!hasScoreA && hasScoreB) return 1;
        
        return 0;
      });

      setResults(fetchedLeads);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocalLeads();
  }, []);

  const updateLeadStatus = async (lead, status) => {
    try {
      const res = await fetch("/api/update-lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sourceFile: lead.sourceFile, name: lead.Name, status }),
      });
      if (res.ok) {
        fetchLocalLeads();
      } else {
        const errorData = await res.json();
        setError(errorData.error || "Failed to update lead.");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleGmailClick = (lead, e) => {
    e.preventDefault();
    const name = lead.Name || 'Inhaber';
    const website = lead.Website || 'Ihrer Website';
    const score = lead['Performance Score'] || 'N/A';
    const address = lead.Address || 'Ihrem Standort';
    const status = lead['Lead Status'] || '';
    
    // Stadt extrahieren
    let city = "Ihrer Region";
    if (address && typeof address === 'string') {
        const parts = address.split(',');
        if (parts.length >= 2) {
            const cityPart = parts[parts.length - 2].trim();
            city = cityPart.replace(/\d+/g, '').trim();
        }
    }

    const lcp = lead.LCP || 'N/A';
    const tbt = lead.TBT || 'N/A';
    const cls = lead.CLS || 'N/A';
    
    let tech_info = "";
    if (lcp !== "N/A" && lcp !== "") {
        tech_info = `Was das für Sie bedeutet:
- Ladezeit (LCP): ${lcp} (Kunden springen oft ab, wenn die Seite nicht sofort lädt)
- Interaktivität (TBT): ${tbt} (Die Zeit, in der die Seite auf Klicks gar nicht reagiert)
- Visuelle Stabilität (CLS): ${cls} (Inhalte springen beim Laden hin und her)
`;
    }

    let subject = "";
    let argument = "";

    if (status.includes("No Website") || website === "None") {
        subject = `Online-Präsenz von ${name} in ${city}`;
        argument = `ich bin neulich auf Ihren Betrieb ${name} aufmerksam geworden. Mir ist dabei aufgefallen, dass Sie aktuell noch keine eigene Website nutzen.\n\nDa ich viel in ${city} unterwegs bin, weiß ich, dass viele Kunden heute zuerst kurz auf dem Handy nachschauen, bevor sie anrufen oder vorbeikommen. Ohne eigene Seite landet man dann oft direkt bei der Konkurrenz, was schade ist.`;
    } else {
        subject = `Technische Analyse der Website von ${name}`;
        let score_display = "nicht optimal";
        if (!isNaN(parseFloat(score))) {
            score_display = `${parseFloat(score).toFixed(0)}/100`;
        }
        const pagespeed_link = `https://pagespeed.web.dev/analysis?url=${website}&strategy=mobile`;
        
        argument = `ich habe mir vorhin kurz die Website von ${name} angeschaut (${website}). Dabei ist mir aufgefallen, dass die mobile Ladezeit aktuell ziemlich bremst.

Google bewertet die Performance auf dem Handy gerade mal mit ${score_display}.

${tech_info}
Das Problem dabei ist weniger die Zahl an sich, sondern dass Google solche langsamen Seiten in den Suchergebnissen oft nach hinten schiebt. Viele Kunden springen auch ab, wenn die Seite auf dem Smartphone nicht sofort lädt.

Hier können Sie den Test von Google selbst einsehen:
${pagespeed_link}`;
    }

    const email_body = `Hallo,

${argument}

Ich bin Dominik Schenitzki, Informatik-Student, und helfe Betrieben hier in der Region dabei, ihren digitalen Auftritt technisch sauber aufzustellen. Mein Fokus liegt dabei auf schnellen, modernen Seiten, die auch wirklich neue Kunden bringen.

Ich biete Ihnen an, dass wir uns Ihre Seite (oder den Plan für eine neue) mal kurz gemeinsam anschauen. Ich gebe Ihnen eine ehrliche Einschätzung zu den Top-Schwachstellen und wie man diese einfach behebt.

Hätten Sie nächste Woche Zeit für ein kurzes Telefonat?

Beste Grüße,

Dominik Schenitzki
https://dtechsolutions.eu/
`;

    // Falls mehrere E-Mails vorhanden sind, nimm die erste
    const firstEmail = (lead.Email || "").split(",")[0].trim();
    
    // Erst synchron das Fenster öffnen (sonst greift der Popup-Blocker!)
    const gmailUrl = `https://mail.google.com/mail/?authuser=dominiksi@dtechsolutions.eu&view=cm&fs=1&to=${firstEmail}&su=${encodeURIComponent(subject)}`;
    window.open(gmailUrl, '_blank');

    // Danach den Text kopieren
    navigator.clipboard.writeText(email_body).catch(() => {});
  };

  const displayedLeads = activeTab === "new" 
    ? results.filter(l => l.Contacted !== 'Yes' && l.Contacted !== 'Rejected') 
    : results.filter(l => l.Contacted === 'Yes' || l.Contacted === 'Rejected');

  const filteredLeads = displayedLeads.filter(lead => {
    const hasEmail = Boolean(lead.Email);
    const hasPhone = Boolean(lead.Phone) && lead.Phone !== "N/A";
    
    if (contactFilter === "all") return true;
    if (contactFilter === "both") return hasEmail && hasPhone;
    if (contactFilter === "email_only") return hasEmail && !hasPhone;
    if (contactFilter === "phone_only") return !hasEmail && hasPhone;
    if (contactFilter === "none") return !hasEmail && !hasPhone;
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans">
      <main className="max-w-7xl mx-auto p-4 md:p-8">
        <header className="mb-10 text-center flex flex-col items-center">
           <h1 className="text-4xl md:text-5xl font-extrabold text-blue-400 mb-2 tracking-tight">
            Animal LeadGen Dashboard <span className="text-3xl">🐾</span>
          </h1>
          <p className="text-gray-400 text-lg mb-4">
            Manage and contact local businesses efficiently.
          </p>
          <button
              onClick={fetchLocalLeads}
              disabled={loading}
              className={`flex items-center space-x-2 font-bold py-2 px-6 rounded-lg shadow-md transition-all duration-300 ${
                loading
                  ? "bg-gray-700 cursor-not-allowed text-gray-400"
                  : "bg-blue-600 hover:bg-blue-500 text-white"
              }`}
            >
              <FaSync className={loading ? "animate-spin" : ""} />
              <span>{loading ? "Lade Daten..." : "Leads aktualisieren (aus CSV)"}</span>
          </button>
        </header>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-4 border-b border-gray-700">
          <button
            onClick={() => setActiveTab("new")}
            className={`flex items-center px-6 py-3 font-semibold text-sm transition-colors ${
              activeTab === "new" 
                ? "border-b-2 border-blue-500 text-blue-400" 
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <FaList className="mr-2" /> Neue Leads ({results.filter(l => l.Contacted !== 'Yes' && l.Contacted !== 'Rejected').length})
          </button>
          <button
            onClick={() => setActiveTab("archive")}
            className={`flex items-center px-6 py-3 font-semibold text-sm transition-colors ${
              activeTab === "archive" 
                ? "border-b-2 border-green-500 text-green-400" 
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <FaArchive className="mr-2" /> Archiv / Kontaktiert ({results.filter(l => l.Contacted === 'Yes' || l.Contacted === 'Rejected').length})
          </button>
        </div>

        {/* Filter Navigation */}
        <div className="flex justify-center mb-8 gap-2 flex-wrap">
          <button onClick={() => setContactFilter("all")} className={`px-4 py-2 text-sm rounded-full transition-colors ${contactFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>Alle anzeigen</button>
          <button onClick={() => setContactFilter("both")} className={`px-4 py-2 text-sm rounded-full transition-colors ${contactFilter === "both" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>📧 + 📞 Beide</button>
          <button onClick={() => setContactFilter("email_only")} className={`px-4 py-2 text-sm rounded-full transition-colors ${contactFilter === "email_only" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>📧 Nur E-Mail</button>
          <button onClick={() => setContactFilter("phone_only")} className={`px-4 py-2 text-sm rounded-full transition-colors ${contactFilter === "phone_only" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>📞 Nur Telefon</button>
          <button onClick={() => setContactFilter("none")} className={`px-4 py-2 text-sm rounded-full transition-colors ${contactFilter === "none" ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>❌ Weder noch</button>
        </div>

        {error && (
          <div className="bg-red-900/50 border-l-4 border-red-500 text-red-200 p-4 rounded-md mb-8 shadow-sm flex items-start space-x-3" role="alert">
            <FaExclamationTriangle className="mt-1 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {filteredLeads.length === 0 && !loading && !error && (
            <div className="text-center py-12 text-gray-500">
                <p className="text-xl">Keine Leads gefunden (Filter überprüfen).</p>
            </div>
        )}

        {filteredLeads.length > 0 && (
          <section className="space-y-6 animate-fade-in-up">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredLeads.map((lead, index) => (
                <article key={index} className="bg-gray-800 shadow-xl rounded-xl overflow-hidden border border-gray-700 hover:shadow-2xl hover:border-gray-600 transition-all duration-300 flex flex-col h-full opacity-90">
                  <div className={`h-2 w-full ${lead.Contacted === 'Yes' ? 'bg-green-600' : (lead['Lead Status'] && lead['Lead Status'].includes('Lead') ? 'bg-blue-500' : 'bg-gray-600')}`}></div>
                  <div className="p-5 flex-grow">
                    <div className="flex justify-between items-start mb-2">
                        <h3 className="font-bold text-lg text-gray-100 line-clamp-2">{lead.Name || "Unbekannt"}</h3>
                        {lead.Contacted === 'Yes' && (
                            <span className="bg-green-900 text-green-300 text-xs px-2 py-1 rounded-full flex items-center border border-green-800">
                                <FaCheck className="mr-1"/> Kontaktiert
                            </span>
                        )}
                        {lead.Contacted === 'Rejected' && (
                            <span className="bg-red-900 text-red-300 text-xs px-2 py-1 rounded-full flex items-center border border-red-800">
                                <FaTimes className="mr-1"/> Abgelehnt
                            </span>
                        )}
                    </div>
                    
                    <p className="text-gray-400 text-xs mb-3 flex items-start">
                      <span className="mr-2 mt-0.5">📍</span>
                      <span className="line-clamp-2">{lead.Address}</span>
                    </p>
                    
                    <div className="flex flex-col gap-2 mb-4">
                        {lead.Phone && (
                            <div className="flex items-center text-xs">
                              <span className="mr-2">📞</span>
                              <a 
                                href={`tel:${lead.Phone.replace(/\\s/g, '')}`} 
                                className="font-mono bg-gray-700 text-blue-400 hover:bg-gray-600 px-3 py-1 rounded flex items-center transition-colors"
                                title="Anrufen"
                              >
                                {lead.Phone}
                              </a>
                            </div>
                        )}
                        {lead.Email && (
                            <div className="flex items-center text-xs">
                              <span className="mr-2">✉️</span>
                              <span className="font-mono bg-gray-700 text-gray-300 px-2 py-1 rounded truncate w-full" title={lead.Email}>{lead.Email}</span>
                            </div>
                        )}
                        {!lead.Email && lead.Phone && activeTab === "new" && (
                           <div className="text-xs text-yellow-500 font-semibold mt-1">
                             ⚠️ Keine E-Mail! Ideal für Kaltakquise per Telefon.
                           </div>
                        )}
                    </div>

                    {lead['Lead Status'] && (
                        <div className="mt-auto p-3 bg-gray-900 rounded-lg border border-gray-700 text-xs">
                            <span className="font-semibold text-gray-300 block mb-1">Status: {lead['Lead Status']}</span>
                            {lead['Performance Score'] && lead['Performance Score'] !== 'N/A' && (
                                <span className="block text-gray-400">PageSpeed: <span className={parseInt(lead['Performance Score']) < 60 ? "text-red-400 font-bold" : "text-green-400 font-bold"}>{lead['Performance Score']}/100</span></span>
                            )}
                            {lead['LCP'] && lead['LCP'] !== 'N/A' && (
                                <span className="block text-gray-400">Ladezeit (LCP): {lead['LCP']}</span>
                            )}
                        </div>
                    )}
                  </div>
                  
                   <div className="bg-gray-900 px-5 py-4 border-t border-gray-700 flex justify-between items-center">
                     {lead.Website && lead.Website.startsWith("http") ? (
                       <a
                         href={lead.Website}
                         target="_blank"
                         rel="noopener noreferrer"
                         className="text-blue-400 text-xs font-semibold flex items-center hover:text-blue-300 transition-colors"
                       >
                         Website <FaExternalLinkAlt className="ml-1 text-[10px]" />
                       </a>
                     ) : (
                       <p className="text-red-400 text-xs font-semibold flex items-center">
                         Keine Website
                       </p>
                     )}
                     
                     <div className="flex gap-2">
                       {lead.Email ? (
                         <button 
                           onClick={(e) => handleGmailClick(lead, e)}
                           className={`${activeTab === 'archive' ? 'bg-gray-700 hover:bg-gray-600' : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-500/20'} text-white text-xs px-4 py-2 rounded-lg font-semibold flex items-center transition-colors`}
                         >
                            <FaEnvelope className="mr-2" /> Gmail (Business)
                         </button>
                       ) : (
                         <button disabled className="bg-gray-800 text-gray-600 text-xs px-4 py-2 rounded-lg font-semibold flex items-center cursor-not-allowed">
                            <FaEnvelope className="mr-2" /> Fehlt
                         </button>
                       )}

                       {activeTab === 'new' && (
                         <>
                           <button
                             onClick={() => updateLeadStatus(lead, 'Yes')}
                             className="bg-green-600 hover:bg-green-500 shadow-lg shadow-green-500/20 text-white text-xs px-3 py-2 rounded-lg font-semibold flex items-center transition-colors"
                             title="Als kontaktiert markieren"
                           >
                             <FaCheck />
                           </button>
                           <button
                             onClick={() => updateLeadStatus(lead, 'Rejected')}
                             className="bg-red-600 hover:bg-red-500 shadow-lg shadow-red-500/20 text-white text-xs px-3 py-2 rounded-lg font-semibold flex items-center transition-colors"
                             title="Kein Interesse (Aussortieren)"
                           >
                             <FaTimes />
                           </button>
                         </>
                       )}
                     </div>
                   </div>
                </article>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
