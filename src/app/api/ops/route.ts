import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import { existsSync } from "fs";
import path from "path";

export async function POST(req: NextRequest): Promise<Response> {
  const { task } = await req.json();

  if (!task) {
    return NextResponse.json({ error: "Task is required" }, { status: 400 });
  }

  const rootDir = process.cwd();
  const venvPython =
    process.platform === "win32"
      ? path.join(rootDir, "orchestrator", "venv", "Scripts", "python.exe")
      : path.join(rootDir, "orchestrator", "venv", "bin", "python");
  const pythonCmd = existsSync(venvPython)
    ? venvPython
    : process.platform === "win32"
      ? "python"
      : "python3";

  // Chama orquestrador Python
  const python = spawn(
    pythonCmd,
    ["-m", "orchestrator.main", "--task", task],
    {
      cwd: rootDir,
      env: {
        ...process.env,
        PYTHONIOENCODING: "utf-8",
      },
    },
  );

  let output = "";
  let error = "";

  python.stdout.on("data", (data) => {
    output += data.toString();
  });

  python.stderr.on("data", (data) => {
    error += data.toString();
  });

  return new Promise<Response>((resolve) => {
    python.on("close", (code) => {
      if (code !== 0) {
        resolve(NextResponse.json({ error, output }, { status: 500 }));
      } else {
        resolve(
          NextResponse.json({
            success: true,
            output,
            workspace: "/workspace/",
          }),
        );
      }
    });
  });
}
