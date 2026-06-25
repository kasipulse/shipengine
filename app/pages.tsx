'use client';
import { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';

export default function HomePage() {
  const [parts, setParts] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    fetch('/api/parts')
      .then((res) => res.json())
      .then((data) => setParts(data))
      .catch((err) => console.error("Error fetching parts:", err));
  }, []);

  // Define your unique categories
  const categories = ['All', 'Engines', 'Gearboxes', 'Electrical', 'Body Parts'];

  // Enhanced Filter: Matches search term AND category (if not 'All')
  const filteredParts = parts.filter((part: any) => {
    const matchesSearch = part.headline.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || part.category_name === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <main className="bg-white min-h-screen">
      <Navbar />
      
      <div className="p-8">
        <h1 className="text-4xl font-bold mb-2 text-slate-800">ShipEngine Inventory</h1>
        <p className="text-slate-500 mb-8">Quality parts for your vehicle needs.</p>
        
        {/* Search and Category Filter Section */}
        <div className="flex flex-col gap-4 mb-8">
          <input 
            type="text"
            placeholder="Search for parts..."
            className="w-full p-4 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 outline-none text-slate-700"
            onChange={(e) => setSearch(e.target.value)}
          />
          
          <div className="flex gap-2 flex-wrap">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-6 py-2 rounded-full font-semibold transition-colors ${
                  selectedCategory === cat 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {filteredParts.map((part: any) => (
            <div key={part.app_id} className="border border-slate-200 bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <h2 className="font-bold text-xl text-blue-600 mb-2">{part.headline}</h2>
              <p className="text-slate-500 mb-4 font-medium">Price: R{part.price_usd}</p>
              <a 
                href={`https://wa.me/27XXXXXXXXX?text=I'm interested in ${part.headline}`} 
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-blue-600 hover:bg-blue-700 text-white text-center py-3 px-4 rounded-lg font-semibold transition-colors"
              >
                WhatsApp Sales
              </a>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
