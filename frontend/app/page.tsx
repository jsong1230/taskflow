export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-zinc-950">
      <main className="flex flex-col items-center gap-8 px-6 text-center">
        <h1 className="text-5xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
          TaskFlow
        </h1>
        <p className="max-w-md text-lg text-zinc-600 dark:text-zinc-400">
          팀 협업을 위한 태스크 관리 플랫폼
        </p>
        <div className="flex gap-4">
          <a
            href="/login"
            className="rounded-lg bg-zinc-900 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-zinc-800 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            시작하기
          </a>
        </div>
      </main>
    </div>
  );
}
