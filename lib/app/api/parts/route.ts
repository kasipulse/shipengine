// app/api/parts/route.ts
import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET(request: Request) {
  // Get search params (e.g., /api/parts?make=Toyota)
  const { searchParams } = new URL(request.url);
  const make = searchParams.get('make');

  try {
    let query = supabase.from('applications').select(`
        app_id, 
        headline, 
        price_usd,
        vehicles(model_name, manufacturer_name)
    `);

    // Add filtering logic
    if (make) {
      query = query.ilike('vehicles.manufacturer_name', `%${make}%`);
    }

    const { data, error } = await query.limit(20);

    if (error) throw error;

    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}