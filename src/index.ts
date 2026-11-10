import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";

function createServer() {
  const server = new McpServer({
    name: "character-studio-mcp",
    version: "0.1.0"
  });

  server.registerTool(
    "create_character_brief",
    {
      description: "Creates a structured design brief for a 3D human, creature, or monster intended for Blender modeling and rigging.",
      inputSchema: {
        name: z.string().min(1).describe("Character name"),
        kind: z.enum(["human", "creature", "monster"]).default("human"),
        style: z.enum(["semi_realistic", "realistic", "stylized"]).default("semi_realistic"),
        description: z.string().min(10).describe("Appearance, anatomy, clothing, materials, and personality"),
        rig: z.enum(["humanoid", "quadruped", "custom"]).default("humanoid")
      }
    },
    async ({ name, kind, style, description, rig }) => {
      const brief = {
        name,
        category: kind,
        visual_style: style,
        modeling_notes: description,
        rig_type: rig,
        production_checklist: [
          "Create clean, deformation-friendly topology",
          "Separate body, clothing, hair, and accessories when useful",
          "Use physically based materials with detailed roughness and normal maps",
          "Create UVs and prepare texture sets",
          "Build an armature matching the selected rig type",
          "Weight-paint and test deformations",
          "Prepare a clean, named Blender collection"
        ],
        export_targets: [".blend", ".fbx", ".glb"]
      };

      return {
        content: [{
          type: "text",
          text: JSON.stringify(brief, null, 2)
        }]
      };
    }
  );

  server.registerTool(
    "list_character_presets",
    {
      description: "Lists starter character categories and recommended rig types.",
      inputSchema: {}
    },
    async () => ({
      content: [{
        type: "text",
        text: JSON.stringify([
          { preset: "survivor", category: "human", rig: "humanoid", notes: "Adult human with practical clothing and believable proportions." },
          { preset: "hospital_patient", category: "human", rig: "humanoid", notes: "Worn hospital clothing, tired posture, realistic anatomy." },
          { preset: "humanoid_monster", category: "monster", rig: "humanoid", notes: "Distorted humanoid anatomy, extended limbs, unsettling silhouette." },
          { preset: "crawler", category: "creature", rig: "custom", notes: "Low crawling creature; requires a custom multi-limb rig." }
        ], null, 2)
      }]
    })
  );

  return server;
}

const handler = createMcpHandler(createServer);

export default {
  fetch(request: Request, env: unknown, ctx: ExecutionContext) {
    if (new URL(request.url).pathname === "/") {
      return new Response("Character Studio MCP is running. Connect using /mcp.", {
        headers: { "content-type": "text/plain; charset=utf-8" }
      });
    }
    return handler(request, env, ctx);
  }
} satisfies ExportedHandler;