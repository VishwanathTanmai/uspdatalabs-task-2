const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('canvas-container').appendChild(renderer.domElement);

// Create specific particles
const geometry = new THREE.BufferGeometry();
const count = 2000;
const positions = new Float32Array(count * 3);

for(let i = 0; i < count * 3; i++) {
    positions[i] = (Math.random() - 0.5) * 10;
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

const material = new THREE.PointsMaterial({
    size: 0.02,
    color: 0x00ff88,
    transparent: true,
    opacity: 0.8
});

const particles = new THREE.Points(geometry, material);
scene.add(particles);

camera.position.z = 3;

// Mouse interaction
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (event) => {
    mouseX = event.clientX / window.innerWidth - 0.5;
    mouseY = event.clientY / window.innerHeight - 0.5;
});

const animate = function () {
    requestAnimationFrame(animate);

    particles.rotation.y += 0.001;
    particles.rotation.x += 0.001;

    // Parallax effect
    particles.rotation.y += mouseX * 0.05;
    particles.rotation.x += mouseY * 0.05;

    renderer.render(scene, camera);
};

animate();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
