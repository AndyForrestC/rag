"use client";

export default function TestPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">
          Frontend Test Page
        </h1>
        <p className="text-gray-600">
          If you can see this, the frontend is working!
        </p>
        <div className="mt-4">
          <button 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={() => alert('Button clicked!')}
          >
            Test Button
          </button>
        </div>
      </div>
    </div>
  );
}
