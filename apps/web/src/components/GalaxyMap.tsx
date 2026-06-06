import './GalaxyMap.css';

import './GalaxyMap.css';

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
  if (!matchState || !matchState.territories) return null;

  const territories = matchState.territories;
  const nodes = Object.keys(territories);

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
    const territory = territories[node];
    const neighbors = territory.neighbors || [];
    for (const neighbor of neighbors) {
      const edgeId = [node, neighbor].sort().join('-');
      if (!drawnEdges.has(edgeId)) {
        drawnEdges.add(edgeId);
        const p1Territory = territories[node];
        const p2Territory = territories[neighbor];
        if (p1Territory && p2Territory) {
          lineElements.push(
            <line 
              key={edgeId} 
              x1={p1Territory.x * 8} y1={p1Territory.y * 6.5} 
              x2={p2Territory.x * 8} y2={p2Territory.y * 6.5} 
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
            const territory = territories[nodeId];
            const color = getPlayerColor(territory.owner_id);
            const isSelected = selectedNode === nodeId;
            const isTarget = targetNode === nodeId;
            const ownerName = territory.owner_id ? matchState.players[territory.owner_id].name : 'Unowned';

            return (
              <g 
                key={nodeId} 
                transform={`translate(${territory.x * 8}, ${territory.y * 6.5})`}
                className={`map-node ${isSelected ? 'selected' : ''} ${isTarget ? 'target' : ''}`}
                onClick={() => onNodeClick(nodeId)}
              >
                <circle r={25} fill={color} className="node-bg" />
                <circle r={25} fill="transparent" stroke={color} className="node-border" />
                
                <text y={5} textAnchor="middle" className="node-troops">
                  {territory.troops}
                </text>
                
                <text y={40} textAnchor="middle" className="node-label">
                  {nodeId}
                </text>
                <text y={55} textAnchor="middle" className="node-owner" fill={color}>
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
