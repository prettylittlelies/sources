export default function Connected() {
  return (
    <main className="min-h-screen flex items-center justify-center pt-24 pb-16 px-4">
      <div className="text-center">
        <h1 className="text-4xl font-medium text-gradient mb-2">Failed!</h1>
        <p className="text-gray-300/90 leading-relaxed">
          An error occurred during linking. Please try again.
        </p>
      </div>
    </main>
  );
}
