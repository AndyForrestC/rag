import Image from "next/image";

export default function Header() {
  return (
    <div className="flex-shrink-0 px-4 py-2 border-t border-gray-100">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-center text-xs text-gray-400">
          <span>Internal Development Use</span>
        </div>
      </div>
    </div>
  );
}
