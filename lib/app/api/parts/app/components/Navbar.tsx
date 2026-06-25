// components/Navbar.tsx
export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-white border-b border-slate-200">
      {/* Text-Logo: Using blue and bold styling */}
      <div className="text-2xl font-black text-blue-600 tracking-tighter">
        SHIP<span className="text-slate-700">ENGINE</span>
      </div>
      
      <div className="flex gap-6 font-medium text-slate-600">
        <a href="/" className="hover:text-blue-600">Inventory</a>
        <a href="#" className="hover:text-blue-600">About</a>
        <a href="#" className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700">Contact</a>
      </div>
    </nav>
  );
}