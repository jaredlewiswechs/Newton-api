/**
 * Newton OS - Main Entry Point
 */

import { boot, Shell, Newton } from './index';
import { TheGraph } from './core/graph';
import { NObjectFactory } from './core/nobject';
import { Inspector } from './apps/inspector';
import { Console } from './apps/console';

// Boot sequence
async function main() {
  const loading = document.getElementById('loading');
  
  // Simulate boot sequence
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Boot Newton OS
  const container = document.getElementById('newton-os')!;
  await boot(container);
  
  // Hide loading screen
  if (loading) {
    loading.classList.add('hidden');
    setTimeout(() => loading.remove(), 500);
  }
  
  // Create some demo objects
  createDemoContent();
  
  // Expose to console for debugging
  (window as any).NewtonOS = {
    Shell,
    Newton,
    TheGraph,
    NObjectFactory,
    Inspector,
    Console,
  };
  
  console.log('[Newton OS] Ready. Access via window.NewtonOS');
}

function createDemoContent() {
  // Create a document
  const doc = NObjectFactory.document('My First Document', 
    'This is a document stored in the Newton OS Object Graph. ' +
    'It has no file path - it exists as a verified NObject.'
  );
  TheGraph.add(doc);
  
  // Create a user
  const user = NObjectFactory.user('Newton User', 'user@newton.os');
  TheGraph.add(user);
  
  // Create relationship: user owns document
  user.addRelationship(doc.id, 'owns');
  
  // Open Inspector after a delay
  setTimeout(() => {
    Inspector.open();
  }, 500);
  
  // Open Newton Console
  setTimeout(() => {
    Console.open();
  }, 1000);
}

// Start
main().catch(console.error);
