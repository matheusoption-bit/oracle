import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";

export async function POST(req: NextRequest) {
  const { task } = await req.json();

  if (!task) {
    return NextResponse.json({ error: "Task is required" }, { status: 400 });
  }

  // Chama orquestrador Python
  const python = spawn(
    "python3",
    ["-m", "orchestrator.main", "--task", task],
    {
      cwd: process.cwd(),
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

  return new Promise((resolve) => {
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
