import React, { useState } from "react";
import { Link } from "react-router-dom";

/* ---------- API ---------- */
const predictFishStock = async (data: any) => {
  const res = await fetch("http://localhost:8000/predict/fish-stock-predictor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) throw new Error("Prediction failed");
  return res.json();
};

/* ---------- FAO VALUES (from your dataset) ---------- */
const AREAS = [
  "Indian Ocean, Eastern",
  "Indian Ocean, Antarctic",
  "Indian Ocean, Western",
];

const COUNTRIES = [
  "Australia",
  "Bahrain",
  "Bangladesh",
  "Belize",
  "British Indian Ocean Ter",
  "Bulgaria",
  "Chile",
  "China",
  "Taiwan Province of China",
  "Comoros",
  "Cook Islands",
  "Djibouti",
  "Egypt",
  "Eritrea",
  "Ethiopia",
  "France",
  "French Southern Terr",
  "Georgia",
  "Germany",
  "Greece",
  "Guinea",
  "Honduras",
  "India",
  "Indonesia",
  "Iran (Islamic Rep. of)",
  "Iraq",
  "Israel",
  "Italy",
  "Japan",
  "Jordan",
  "Kenya",
  "Korea, Republic of",
  "Kuwait",
  "Lithuania",
  "Madagascar",
  "Malaysia",
  "Maldives",
  "Mauritius",
  "Mayotte",
  "Mozambique",
  "Myanmar",
  "Namibia",
  "New Zealand",
  "Norway",
  "Oman",
  "Pakistan",
  "Philippines",
  "Poland",
  "Portugal",
  "Qatar",
  "Réunion",
  "Romania",
  "Russian Federation",
  "Saudi Arabia",
  "Senegal",
  "Seychelles",
  "Somalia",
  "South Africa",
  "Spain",
  "Sri Lanka",
  "Sudan (former)",
  "Sudan",
  "Tanzania, United Rep. of",
  "Thailand",
  "Timor-Leste",
  "Ukraine",
  "Un. Sov. Soc. Rep.",
  "United Arab Emirates",
  "United Kingdom",
  "Uruguay",
  "Vanuatu",
  "Yemen",
  "United Republic of Tanzania, Zanzibar",
  "Other nei"
];
const SPECIES = [
  "Perca fluviatilis", "Anguilla australis", "Anguilla reinhardtii", "Lates calcarifer",
  "Pleuronectiformes", "Rhombosolea spp", "Gadiformes", "Muraenolepis spp",
  "Muraenolepis microps", "Antimora rostrata", "Macruronus novaezelandiae", "Macrouridae",
  "Macrourus spp", "Macrourus whitsoni", "Macrourus carinatus", "Macrourus holotrachys",
  "Macrourus caml", "Cynomacrurus piriei", "Alepisaurus spp", "Ariidae",

  "Mugilidae", "Percoidei", "Serranidae", "Plectropomus leopardus",
  "Priacanthus macracanthus", "Apogonidae", "Sillaginidae", "Arripis georgianus",
  "Arripis trutta", "Lutjanidae", "Haemulidae (=Pomadasyidae)", "Argyrosomus hololepidotus",

  "Lethrinus nebulosus", "Lethrinus olivaceus", "Sparidae", "Pagrus auratus",
  "Girella tricuspidata", "Labridae", "Polynemidae", "Nototheniidae",
  "Notothenia rossii", "Gobionotothen acuta", "Lepidonotothen squamifrons", "Lindbergichthys mizops",

  "Trematomus spp", "Pleuragramma antarctica", "Acanthuridae", "Platycephalidae",
  "Platycephalus arenarius", "Tetraodontidae", "Monacanthidae", "Batrachoides spp",
  "Alepocephalus spp", "Myctophidae", "Nannobrachium achirus", "Genypterus blacodes",

  "Beryx spp", "Centroberyx affinis", "Hoplostethus atlanticus", "Zeidae",
  "Zeus faber", "Zenopsis nebulosus", "Neocyttus rhomboidalis", "Pseudocyttus maculatus",

  "Nemadactylus spp", "Latridae", "Dissostichus mawsoni", "Dissostichus eleginoides",
  "Channichthyidae", "Chionobathyscus dewitti", "Chaenocephalus aceratus", "Champsocephalus gunnari",

  "Pseudochaenichthys georgianus", "Chionodraco rastrospinosus", "Channichthys rhinoceratus",
  "Chaenodraco wilsoni", "Thyrsites atun", "Rexea solandri", "Lepidopus caudatus",

  "Centrolophidae", "Centrolophus niger", "Seriolella spp", "Seriolella brama",
  "Seriolella punctata", "Seriolella caerulea", "Hyperoglyphe antarctica", "Scorpaenidae",

  "Helicolenus percoides", "Chelidonichthys kumu", "Lepidotrigla vanessa", "Pterygotrigla polyommata",
  "Zanclorhynchus spinifer", "Perciformes", "Clupeoidei", "Engraulidae",

  "Scombroidei", "Sarda australis", "Acanthocybium solandri", "Scomberomorus spp",
  "Scomberomorus commerson", "Scomberomorus semifasciatus", "Euthynnus affinis", "Katsuwonus pelamis",

  "Thunnus tonggol", "Thunnus alalunga", "Thunnus maccoyii", "Thunnus albacares",
  "Thunnus obesus", "Istiophoridae", "Istiophorus platypterus", "Makaira nigricans",

  "Istiompax indica", "Kajikia audax", "Tetrapturus angustirostris", "Xiphias gladius",

    "Hemiramphidae", "Hemiramphus spp", "Lampris immaculatus", "Trachipterus spp",
  "Trachipterus jacksonensis", "Pomatomus saltatrix", "Trachurus picturatus",
  "Trachurus declivis", "Pseudocaranx dentex", "Seriola spp",

  "Seriola lalandi", "Coryphaena hippurus", "Scombridae", "Scomber australasicus",
  "Mola spp", "Lamna nasus", "Mustelus antarcticus", "Galeorhinus galeus",

  "Somniosus pacificus", "Centrophorus spp", "Etmopterus spp",
  "Pristiophorus spp", "Squatinidae", "Rajiformes", "Bathyraja spp",

  "Bathyraja eatonii", "Bathyraja maccaini", "Bathyraja murrayi",
  "Bathyraja irrasa", "Amblyraja georgiana", "Amblyraja taaf",

  "Callorhinchidae", "Callorhinchus milii", "Elasmobranchii",
  "Actinopterygii", "Euastacus armatus", "Portunus pelagicus",

  "Panulirus spp", "Panulirus cygnus", "Jasus novaehollandiae",
  "Scyllaridae", "Metanephrops spp", "Anomura", "Lithodidae",

  "Penaeus spp", "Penaeus merguiensis", "Penaeus monodon",
  "Metapenaeus macleayi", "Metapenaeus endeavouri", "Metapenaeus dalli",

  "Stomatopoda", "Crustacea", "Mollusca", "Gastropoda",
  "Haliotis spp", "Haliotis rubra", "Mytilus planulatus",

  "Pectinidae", "Pecten fumatus", "Paphies australis",
  "Cephalopoda", "Sepiidae, Sepiolidae", "Loliginidae, Ommastrephidae",

  "Octopodidae", "Ascidiacea", "Salpidae", "Echinodermata",
  "Asteroidea", "Echinoidea", "Strongylocentrotus spp",

  "Arbacia lixula", "Echinometra vanbrunti", "Holothuroidea",
  "Bohadschia argus", "Rhopilema spp", "Invertebrata",

  "Ex Pinctada spp", "Pinctada maxima", "Cnidaria", "Hydrozoa",
  "Anthoathecata", "Stylasteridae", "Scleractinia",

  "Antipatharia", "Actiniaria", "Alcyonacea", "Pennatulacea",
  "Gorgoniidae", "Porifera", "Hexactinellida", "Demospongiae",

  "Spongiidae", "Phaeophyceae", "Nematalosa nasus", "Chanos chanos",
  "Bothus pantherinus", "Synodontidae", "Netuma thalassina",

  "Epinephelus spp", "Epinephelus polylepis", "Pelates quadrilineatus",
  "Lutjanus argentimaculatus", "Nemipteridae", "Diagramma pictum",

  "Plectorhinchus pictus", "Plectorhinchus sordidus",
  "Pomadasys stridens", "Lethrinidae", "Lethrinus lentjan",

  "Lethrinus microdon", "Cheimerius nufar", "Rhabdosargus haffara",
  "Sparidentex hasta", "Acanthopagrus berda",
  "Acanthopagrus bifasciatus",

  "Mullidae", "Gerres spp", "Scaridae", "Pomacanthus maculosus",
  "Platax spp", "Siganus spp", "Ariomma indicum", "Sardinella spp",

];


/* ---------- COMPONENT ---------- */
const FishStockPredictor = () => {
  const [formData, setFormData] = useState({
    period: "",
    area: "",
    country: "",
    scientific_name: "",
  });

  const [prediction, setPrediction] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await predictFishStock({
        PERIOD: Number(formData.period),
        Area: formData.area,
        Country: formData.country,
        Scientific_Name: formData.scientific_name,
      });

      setPrediction(result.predicted_value);
    } catch {
      setError("Prediction failed. Please check inputs.");
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* NAV */}
      <nav className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center">
          <span className="text-xl font-bold text-cyan-600">MARLIN</span>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <Link to="/models" className="text-cyan-600 mb-6 inline-block">
          ← Back to ML Models
        </Link>

        {/* HEADER */}
        <div className="bg-gradient-to-r from-teal-500 to-cyan-600 rounded-2xl p-8 text-white mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Fish Stock Quantity Predictor
          </h1>
          <p className="text-cyan-100">
            Predict annual fish stock quantity (metric tonnes) using FAO data
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* FORM */}
          <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-2xl font-bold mb-6">Prediction Inputs</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* YEAR */}
              <input
                name="period"
                type="number"
                placeholder="Year (e.g. 2018)"
                className="w-full border rounded-lg px-4 py-3"
                onChange={handleChange}
                required
              />

              {/* AREA */}
              <input
                name="area"
                list="areas"
                placeholder="FAO Area (type to search)"
                className="w-full border rounded-lg px-4 py-3"
                onChange={handleChange}
                required
              />
              <datalist id="areas">
                {AREAS.map((a) => (
                  <option key={a} value={a} />
                ))}
              </datalist>

              {/* COUNTRY */}
              <input
                name="country"
                list="countries"
                placeholder="Country (type to search)"
                className="w-full border rounded-lg px-4 py-3"
                onChange={handleChange}
                required
              />
              <datalist id="countries">
                {COUNTRIES.map((c) => (
                  <option key={c} value={c} />
                ))}
              </datalist>

              {/* SPECIES */}
              <input
                name="scientific_name"
                list="species"
                placeholder="Scientific name (type to search)"
                className="w-full border rounded-lg px-4 py-3"
                onChange={handleChange}
                required
              />
              <datalist id="species">
                {SPECIES.map((s) => (
                  <option key={s} value={s} />
                ))}
              </datalist>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-cyan-600 text-white py-3 rounded-lg hover:bg-cyan-700"
              >
                {loading ? "Predicting..." : "Predict Fish Stock"}
              </button>
            </form>
          </div>

          {/* RESULT */}
          <div className="bg-white rounded-xl p-6 shadow-sm border text-center">
            <h3 className="text-xl font-bold mb-4">Prediction Result</h3>

            {prediction !== null ? (
              <>
                <div className="text-4xl font-bold text-green-600 mb-2">
                  {prediction.toLocaleString()} MT
                </div>
                <p className="text-gray-600">
                  Estimated annual fish stock quantity
                </p>
              </>
            ) : (
              <p className="text-gray-500">No prediction yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FishStockPredictor;
