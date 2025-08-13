import fs from 'fs';
import path from 'path';

function replaceAllImports(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      replaceAllImports(filePath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      let content = fs.readFileSync(filePath, 'utf8');
      
      // Calculer le chemin relatif basé sur la profondeur du fichier
      const relativePath = filePath.split('src')[1];
      const depth = (relativePath.match(/\//g) || []).length - 1;
      const relativePrefix = '../'.repeat(depth);
      
      // Remplacer TOUS les imports @/ par des chemins relatifs
      content = content.replace(/from ['"]@\//g, `from '${relativePrefix}`);
      content = content.replace(/import\s+['"]@\//g, `import '${relativePrefix}`);
      
      fs.writeFileSync(filePath, content);
      console.log(`Fixed ALL imports in: ${filePath}`);
    }
  });
}

// Démarrer depuis le dossier src
replaceAllImports('./src');
console.log('All @ imports fixed!');
