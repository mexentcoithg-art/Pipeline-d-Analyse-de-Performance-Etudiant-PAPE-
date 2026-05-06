const fs = require('fs');
const path = require('path');

const lucidePath = path.join(__dirname, 'client', 'node_modules', 'lucide-react', 'dist', 'lucide-react.cjs.js');

try {
    const content = fs.readFileSync(lucidePath, 'utf8');
    console.log("Found LayoutList? ", content.includes('LayoutList'));
    console.log("Found Columns3? ", content.includes('Columns3'));
    console.log("Found Settings2? ", content.includes('Settings2'));
    console.log("Found Table2? ", content.includes('Table2'));
} catch (e) {
    console.error("Could not read lucide-react module", e.message);
}
