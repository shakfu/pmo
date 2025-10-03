function NotFoundView() {
  return (
    <div className="rounded-lg bg-white p-6 shadow">
      <h1 className="text-2xl font-semibold text-slate-900">Page not found</h1>
      <p className="mt-2 text-sm text-slate-600">
        The screen you are looking for does not exist. Use the navigation to find your way back.
      </p>
    </div>
  );
}

export default NotFoundView;
