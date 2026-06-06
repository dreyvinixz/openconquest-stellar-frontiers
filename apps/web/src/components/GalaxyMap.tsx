import './GalaxyMap.css';

// Coordenadas fixas baseadas no default_galaxy do backend
const GALAXY_NODES = {
  N1: { x: 400, y: 100 },
  N2: { x: 250, y: 250 },
  N3: { x: 550, y: 250 },
  N4: { x: 250, y: 450 },
  N5: { x: 550, y: 450 },
  N6: { x: 400, y: 550 },
  N7: { x: 700, y: 450 },
};

const PLAYER_COLORS = [
  'var(--primary-cyan)',
  'var(--accent-purple)',
  'var(--danger-red)',
  'var(--success-green)',
  '#f59e0b',
  '#ec4899'
];

interface GalaxyMapProps {
  matchState: any;
  selectedNode: string | null;
  targetNode: string | null;
  onNodeClick: (nodeId: string) => void;
}

export function GalaxyMap({ matchState, selectedNode, targetNode, onNodeClick }: GalaxyMapProps) {
  if (!matchState || !matchState.board) return null;

  const territories = matchState.board.territories;
  const nodes = Object.keys(territories);
  const edges = matchState.board.edges;

  // Map player IDs to stable colors
  const playerIds = Object.keys(matchState.players).sort();
  const getPlayerColor = (playerId: string) => {
    if (!playerId) return '#555'; // Unowned or unknown
    const idx = playerIds.indexOf(playerId);
    return PLAYER_COLORS[idx % PLAYER_COLORS.length];
  };

  // Dedup edges for drawing lines
  const drawnEdges = new Set<string>();
  const lineElements = [];

  for (const node of nodes) {
    for (const neighbor of edges[node]) {
      const edgeId = [node, neighbor].sort().join('-');
      if (!drawnEdges.has(edgeId)) {
        drawnEdges.add(edgeId);
        const p1 = GALAXY_NODES[node as keyof typeof GALAXY_NODES];
        const p2 = GALAXY_NODES[neighbor as keyof typeof GALAXY_NODES];
        if (p1 && p2) {
          lineElements.push(
            <line 
              key={edgeId} 
              x1={p1.x} y1={p1.y} 
              x2={p2.x} y2={p2.y} 
              className="map-edge"
            />
          );
        }
      }
    }
  }

  return (
    <div className="galaxy-map-container">
      <svg viewBox="0 0 800 650" className="galaxy-svg">
        {/* Draw Edges */}
        <g className="edges">{lineElements}</g>

        {/* Draw Nodes */}
        <g className="nodes">
          {nodes.map(nodeId => {
            const pos = GALAXY_NODES[nodeId as keyof typeof GALAXY_NODES];
            if (!pos) return null;
            
            const territory = territories[nodeId];
            const color = getPlayerColor(territory.owner_id);
            const isSelected = selectedNode === nodeId;
            const isTarget = targetNode === nodeId;
            const ownerName = territory.owner_id ? matchState.players[territory.owner_id].name : 'Unowned';

            return (
              <g 
                key={nodeId} 
                transform={`translate(${pos.x}, ${pos.y})`}
                className={`map-node ${isSelected ? 'selected' : ''} ${isTarget ? 'target' : ''}`}
                onClick={() => onNodeClick(nodeId)}
              >
                <circle r={30} fill={color} className="node-bg" />
                <circle r={30} fill="transparent" stroke={color} className="node-border" />
                
                <text y={5} textAnchor="middle" className="node-troops">
                  {territory.troops}
                </text>
                
                <text y={45} textAnchor="middle" className="node-label">
                  {nodeId}
                </text>
                <text y={60} textAnchor="middle" className="node-owner" fill={color}>
                  {ownerName}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
