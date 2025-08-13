import fs from 'fs';
import path from 'path';

function replaceImports(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      replaceImports(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      let content = fs.readFileSync(filePath, 'utf8');
      
      // Remplacer les imports @/lib/ par des chemins relatifs
      content = content.replace(/from ['"]@\/lib\/api['"]/g, (match, offset) => {
        // Calculer le chemin relatif basé sur la profondeur du fichier
        const relativePath = filePath.split('src')[1];
        const depth = (relativePath.match(/\//g) || []).length - 1;
        const relativePrefix = '../'.repeat(depth);
        return `from '${relativePrefix}lib/api'`;
      });
      
      content = content.replace(/from ['"]@\/lib\/utils['"]/g, (match, offset) => {
        const relativePath = filePath.split('src')[1];
        const depth = (relativePath.match(/\//g) || []).length - 1;
        const relativePrefix = '../'.repeat(depth);
        return `from '${relativePrefix}lib/utils'`;
      });
      
      fs.writeFileSync(filePath, content);
      console.log(`Fixed imports in: ${filePath}`);
    }
  });
}

// Démarrer depuis le dossier src
replaceImports('./src');
console.log('All imports fixed!');
