// Copilot code
/**
 * OpenAI MCP Example: File Reader Agent
 * 
 * This agent can read and list files in a directory using MCP.
 * No custom file handling code needed!
 * 
 * Prerequisites:
 * 1. npm install @openai/agents
 * 2. export OPENAI_API_KEY="your-key"
 * 
 * Run:
 * npx tsx openai_file_reader.ts
 */

import { Agent, run, MCPServerStdio } from '@openai/agents';
import * as path from 'node:path';

async function main() {
  console.log('🚀 Starting File Reader Agent with MCP...\n');

  // Get current directory
  const currentDir = process.cwd();
  console.log(`📁 Working directory: ${currentDir}\n`);

  // Connect to filesystem MCP server
  console.log('🔌 Connecting to filesystem MCP server...');
  const fileServer = new MCPServerStdio({
    name: 'Filesystem MCP Server',
    fullCommand: `npx -y @modelcontextprotocol/server-filesystem ${currentDir}`,
  });

  try {
    await fileServer.connect();
    console.log('✅ MCP server connected!\n');

    // Create agent
    const agent = new Agent({
      name: 'File Assistant',
      instructions: `You are a helpful file assistant. 
You can list files, read file contents, and search for files.
Always be concise and helpful.`,
      mcpServers: [fileServer],
    });

    console.log('🤖 Agent created! Running queries...\n');
    console.log('─'.repeat(60));

    // Query 1: List all markdown files
    console.log('\n📝 Query 1: List all markdown files\n');
    const result1 = await run(
      agent,
      'List all .md files in the current directory. Show just the filenames.'
    );
    console.log('Answer:', result1.finalOutput);

    console.log('\n' + '─'.repeat(60));

    // Query 2: Read README.md (first 500 characters)
    console.log('\n📖 Query 2: Read README.md summary\n');
    const result2 = await run(
      agent,
      'Read the README.md file and give me a one-sentence summary of what it explains.'
    );
    console.log('Answer:', result2.finalOutput);

    console.log('\n' + '─'.repeat(60));

    // Query 3: Search for Python files
    console.log('\n🐍 Query 3: Find Python files\n');
    const result3 = await run(
      agent,
      'Are there any Python files in this directory? List them if yes.'
    );
    console.log('Answer:', result3.finalOutput);

    console.log('\n' + '─'.repeat(60));
    console.log('\n✨ Demo complete! The agent used MCP to access files automatically.\n');

  } catch (error) {
    console.error('❌ Error:', error);
    if (error instanceof Error) {
      console.error('Details:', error.message);
      
      if (error.message.includes('OPENAI_API_KEY')) {
        console.error('\n💡 Fix: Set your API key with:');
        console.error('   export OPENAI_API_KEY="sk-your-key-here"');
      }
    }
  } finally {
    // Always close the MCP server
    console.log('\n🔌 Closing MCP server...');
    await fileServer.close();
    console.log('✅ Done!');
  }
}

// Run the example
main().catch(console.error);
