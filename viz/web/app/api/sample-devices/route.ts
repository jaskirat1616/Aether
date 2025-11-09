import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    devices: [
      { ip: "192.168.1.10", distance: 3.4 },
      { ip: "192.168.1.11", distance: 5.2 }
    ]
  });
}

