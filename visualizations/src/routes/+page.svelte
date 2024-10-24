<script lang="ts">
	import ColorThief from 'colorthief';
	export let data;

	let movies = data.data;

	// sort by opening_weekend_revenue
	movies.sort((a, b) => b.opening_weekend_revenue - a.opening_weekend_revenue);

	// get top 20
	movies = movies.slice(0, 20);

	let movie_images = movies.map((movie) => null);

	const remove_thumbnail = (image_src: string) => {
		if (image_src.includes('-Thumbnail.jpg')) {
			return image_src.replace('-Thumbnail.jpg', '.jpg');
		} else {
			return image_src;
		}
	};

	const format_to_millions = (revenue: number) => {
		return (revenue / 1000000).toFixed(2) + 'M';
	};

	const getColor = (img: HTMLImageElement) => {
		const colorThief = new ColorThief();
		const color = colorThief.getPalette(img, 2)[0];
		console.log(color);
		return color;
	};
</script>

<h1 class="text-3xl font-bold">Top 20 Movies by Opening Weekend Revenue</h1>
<div class="grid grid-cols-8 gap-2">
	{#each movies as movie, i}
		<div class="card p-1" style="background-color: white">
			<h2 class="text-3xl">{i + 1}: <span class="font-semibold">{movie.title}</span></h2>
			<p class="text-xl">
				Opening Weekend Revenue: <span class="font-semibold"
					>${format_to_millions(movie.opening_weekend_revenue)}</span
				>
			</p>
		</div>
		<img
			src={remove_thumbnail(movie.poster)}
			alt={movie.title}
			bind:this={movie_images[i]}
			on:load={(img) => getColor(img.target)}
		/>
	{/each}
</div>
